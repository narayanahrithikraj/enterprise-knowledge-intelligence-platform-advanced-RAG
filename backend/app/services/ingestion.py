import os
from typing import List, Dict, Any
from pypdf import PdfReader
import docx
import openpyxl

class EnterpriseIngestionService:
    def extract_raw_text(self, file_path: str, extension: str) -> str:
        """Extracts text contents based on target application format rules."""
        text = ""
        
        # 1. Native PDF Parsing
        if extension == "PDF":
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        # 2. Microsoft Word Document Parsing
        elif extension == "DOCX":
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
        # 3. Microsoft Excel Sheet Table Tabulation
        elif extension == "XLSX":
            wb = openpyxl.load_workbook(file_path, data_only=True)
            text_lines = []
            for sheet in wb.worksheets:
                text_lines.append(f"--- Sheet: {sheet.title} ---")
                for row in sheet.iter_rows(values_only=True):
                    row_str = " | ".join([str(cell) for cell in row if cell is not None])
                    if row_str.strip():
                        text_lines.append(row_str)
            text = "\n".join(text_lines)
            
        # 4. Plain Text File Parsing Fallback Loop
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                
        return text

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts text, splits it into semantic parents, and maps high-retention child fragments."""
        filename = os.path.basename(file_path)
        ext = filename.split(".")[-1].upper() if "." in filename else "TXT"
        
        raw_content = self.extract_raw_text(file_path, ext)
        if not raw_content.strip():
            return []

        processed_blocks = []
        
        # Split document text into large context blocks (Parent Context Nodes)
        paragraphs = [p.strip() for p in raw_content.split("\n\n") if p.strip()]
        
        for p_idx, para in enumerate(paragraphs):
            # If paragraph text string length is short, avoid fragmentation loops
            if len(para) < 200:
                child_chunks = [para]
            else:
                # Segment paragraph into smaller semantic child sentences
                child_chunks = [para[i:i+250] for i in range(0, len(para), 200)]
            
            children_payload = []
            for c_idx, chunk in enumerate(child_chunks):
                children_payload.append({
                    "child_id": f"{filename}_p{p_idx}_c{c_idx}",
                    "text": chunk,
                    "metadata": {
                        "filename": filename,
                        "source": f"{filename} - Block {p_idx}"
                    }
                })
                
            processed_blocks.append({
                "parent_text": para,
                "children": children_payload
            })
            
        return processed_blocks