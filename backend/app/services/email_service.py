"""
Email service for sending automated reports.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        smtp_use_ssl: bool,
        from_email: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_use_ssl = smtp_use_ssl
        self.from_email = from_email

    def send_report_email(
        self,
        subject: str,
        body_html: str,
        recipients: List[str],
        task_name: str = "",
    ) -> bool:
        """
        Send an email report to the specified recipients.

        Args:
            subject: Email subject
            body_html: HTML body content
            recipients: List of recipient email addresses
            task_name: Name of the scheduled task (for logging)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Attach HTML body
            html_part = MIMEText(body_html, "html", "utf-8")
            msg.attach(html_part)

            # Send email
            logger.info(
                f"Sending email for task '{task_name}' to {len(recipients)} recipient(s)"
            )

            # IMPORTANT: Port 25 typically uses STARTTLS, not direct SSL
            # Direct SSL is typically on port 465
            # Port 587 also uses STARTTLS
            try:
                if self.smtp_use_ssl and self.smtp_port == 465:
                    # Use direct SSL connection (port 465)
                    with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                        server.login(self.smtp_username, self.smtp_password)
                        server.send_message(msg)
                else:
                    # Use STARTTLS connection (port 25, 587, or others)
                    with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                        # For port 25/587, use STARTTLS
                        if self.smtp_port in (25, 587):
                            server.starttls()
                        server.login(self.smtp_username, self.smtp_password)
                        server.send_message(msg)
            except Exception as smtp_error:
                logger.error(f"SMTP connection failed: {smtp_error}")
                raise


            logger.info(f"Email sent successfully for task '{task_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to send email for task '{task_name}': {str(e)}")
            return False

    def format_report_html(
        self,
        task_name: str,
        prompt: str,
        agent_name: str,
        response: str,
        execution_time: str,
    ) -> str:
        """
        Format the agent response as HTML email.

        Args:
            task_name: Name of the scheduled task
            prompt: The question/prompt that was executed
            agent_name: Name of the agent used
            response: Agent's response
            execution_time: Timestamp of execution

        Returns:
            HTML formatted email body
        """
        # Convert markdown tables to HTML if present
        response_html = self._markdown_to_html(response)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .info-box {{
                    background-color: #f5f5f5;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .info-box strong {{
                    color: #4CAF50;
                }}
                .response {{
                    background-color: white;
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 5px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Report Automatico: {task_name}</h1>
            </div>

            <div class="info-box">
                <p><strong>Agente:</strong> {agent_name}</p>
                <p><strong>Data esecuzione:</strong> {execution_time}</p>
                <p><strong>Domanda:</strong></p>
                <p style="font-style: italic; margin-left: 20px;">"{prompt}"</p>
            </div>

            <div class="response">
                <h2>Risposta</h2>
                {response_html}
            </div>

            <div class="footer">
                <p>Questo è un report automatico generato dal sistema DatapizzaAgent.</p>
                <p>Per modificare le impostazioni di questa schedulazione, accedi al pannello admin.</p>
            </div>
        </body>
        </html>
        """
        return html

    def _markdown_to_html(self, text: str) -> str:
        """
        Convert markdown-style tables and formatting to HTML.

        Args:
            text: Markdown text

        Returns:
            HTML formatted text
        """
        import re

        lines = text.split("\n")
        html_lines = []
        in_table = False
        table_rows = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect markdown table
            if stripped.startswith("|") and "|" in stripped[1:]:
                if not in_table:
                    in_table = True
                    table_rows = []

                # Skip separator line (| --- | --- |)
                if i > 0 and set(stripped.replace("|", "").strip()) <= set("- :"):
                    continue

                # Parse table row
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                table_rows.append(cells)

            else:
                # If we were in a table, render it
                if in_table:
                    html_lines.append(self._render_table(table_rows))
                    table_rows = []
                    in_table = False

                # Regular text formatting
                if stripped:
                    # Bold
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    # Italic
                    line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
                    # Code
                    line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)

                    html_lines.append(f"<p>{line}</p>")
                else:
                    html_lines.append("<br>")

        # Render final table if still in table mode
        if in_table and table_rows:
            html_lines.append(self._render_table(table_rows))

        return "\n".join(html_lines)

    def _render_table(self, rows: List[List[str]]) -> str:
        """
        Render table rows as HTML table.

        Args:
            rows: List of table rows, first row is header

        Returns:
            HTML table
        """
        if not rows:
            return ""

        html = ["<table>"]

        # Header
        if rows:
            html.append("<thead><tr>")
            for cell in rows[0]:
                html.append(f"<th>{cell}</th>")
            html.append("</tr></thead>")

        # Body
        if len(rows) > 1:
            html.append("<tbody>")
            for row in rows[1:]:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</tbody>")

        html.append("</table>")
        return "\n".join(html)
