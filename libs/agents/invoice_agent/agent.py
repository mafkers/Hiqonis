import logging
import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.antigravity import Agent as AGYAgent, LocalAgentConfig
from sqlalchemy.future import select

from libs.infrastructure.database.session import AsyncSessionLocal
from libs.infrastructure.database.models import Contact, Invoice, InvoiceItem, InvoiceStatus

logger = logging.getLogger("hiqonis.invoice_agent")

# --- Define Invoice Tool Functions for Google Antigravity Agent ---

async def create_invoice_tool(
    tenant_id: str,
    contact_id: str,
    items: List[Dict[str, Any]],
    invoice_number: Optional[str] = None
) -> str:
    """Creates a new invoice in the database with multiple items.

    Args:
        tenant_id: The ID of the tenant.
        contact_id: The ID of the contact.
        items: List of dict items. Each item MUST have:
               - description: str
               - quantity: int
               - unit_price: float
        invoice_number: Optional custom invoice number. Generated automatically if not provided.
    """
    if not items:
        return "Error: Invoice items cannot be empty."

    # Validate items structure
    parsed_items = []
    total_amount = 0.0
    for it in items:
        desc = it.get("description")
        qty = int(it.get("quantity", 1))
        price = float(it.get("unit_price", 0.0))
        if not desc:
            return "Error: Each item must have a non-empty description."
        amount = qty * price
        total_amount += amount
        parsed_items.append({
            "description": desc,
            "quantity": qty,
            "unit_price": price,
            "amount": amount
        })

    if not invoice_number:
        # Generate clean invoice number
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    async with AsyncSessionLocal() as db:
        try:
            # Create Invoice
            invoice = Invoice(
                tenant_id=tenant_id,
                contact_id=contact_id,
                invoice_number=invoice_number,
                status=InvoiceStatus.PENDING,
                total_amount=total_amount
            )
            db.add(invoice)
            await db.flush()  # Populates invoice.id

            # Create InvoiceItems
            for pit in parsed_items:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=pit["description"],
                    quantity=pit["quantity"],
                    unit_price=pit["unit_price"],
                    amount=pit["amount"]
                )
                db.add(item)
            
            await db.commit()
            return f"Successfully created invoice. Invoice ID: {invoice.id}, Invoice Number: {invoice_number}, Total: {total_amount}"
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error in create_invoice_tool: {str(e)}")
            return f"Failed to create invoice: {str(e)}"

async def generate_invoice_pdf_tool(invoice_id: str) -> str:
    """Compiles a beautiful invoice details page / PDF file and stores it locally.

    Args:
        invoice_id: The database ID of the invoice.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Query invoice along with items and contact info
            result = await db.execute(select(Invoice).filter(Invoice.id == invoice_id))
            invoice = result.scalars().first()
            if not invoice:
                return f"Error: Invoice with ID {invoice_id} not found."

            # Query items
            result_items = await db.execute(select(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id))
            items = result_items.scalars().all()

            # Query contact
            result_contact = await db.execute(select(Contact).filter(Contact.id == invoice.contact_id))
            contact = result_contact.scalars().first()

            contact_name = contact.name if contact else "Walk-in Customer"
            contact_email = contact.email if contact else "N/A"

            # Create beautiful invoice text representation
            invoice_lines = [
                "==================================================",
                "                 HIQONIS INVOICE                  ",
                "==================================================",
                f"Invoice Number: {invoice.invoice_number}",
                f"Invoice Date:   {invoice.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Status:         {invoice.status.value.upper()}",
                "--------------------------------------------------",
                f"Billed To:      {contact_name}",
                f"Email:          {contact_email}",
                "==================================================",
                f"{'Item Description':<25} | {'Qty':<3} | {'Price':<8} | {'Total':<8}",
                "--------------------------------------------------"
            ]

            for it in items:
                desc = it.description[:24]
                qty = it.quantity
                price = f"{it.unit_price:.2f}"
                amount = f"{it.amount:.2f}"
                invoice_lines.append(f"{desc:<25} | {qty:<3} | {price:<8} | {amount:<8}")

            invoice_lines.append("--------------------------------------------------")
            invoice_lines.append(f"{'TOTAL DUE:':<38} | USD {invoice.total_amount:.2f}")
            invoice_lines.append("==================================================")
            invoice_lines.append("         Thank you for your business!            ")
            invoice_lines.append("==================================================")

            invoice_text = "\n".join(invoice_lines)

            # Define path and save
            storage_dir = "/home/momo/Dokumen/Insyaallah Sukses/storage/invoices"
            os.makedirs(storage_dir, exist_ok=True)
            file_path = os.path.join(storage_dir, f"invoice_{invoice.invoice_number}.pdf")

            with open(file_path, "w") as f:
                f.write(invoice_text)

            return f"Successfully generated invoice PDF at: {file_path}"
        except Exception as e:
            logger.exception(f"Error in generate_invoice_pdf_tool: {str(e)}")
            return f"Failed to generate invoice PDF: {str(e)}"

# --- Define the HiqonisInvoiceAgent Wrapper ---

class HiqonisInvoiceAgent:
    """AI Invoice Agent driving invoice extraction and compilation from chat conversations."""
    
    def __init__(self, tenant_id: str, api_key: Optional[str] = None):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.system_instructions = (
            f"You are an automated invoicing assistant for tenant '{tenant_id}'. "
            "Your goal is to parse user conversations, extract invoice line items (description, quantity, price), "
            "and create a formal invoice in the CRM database using the 'create_invoice_tool'. "
            "After creating the invoice, you must generate/compile the PDF version using 'generate_invoice_pdf_tool'. "
            "Always be precise with quantities, prices, and totals. Execute tools when sufficient data is collected."
        )

    async def analyze_and_invoice(self, conversation_history: str, contact_id: str) -> str:
        """Parse conversation, create an invoice, and generate its PDF representation."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            tools=[create_invoice_tool, generate_invoice_pdf_tool],
            model="gemini-2.5-flash",
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(
                f"Analyze this conversation thread for contact '{contact_id}' and invoice them accordingly:\n\n{conversation_history}"
            )
            return await response.text()
