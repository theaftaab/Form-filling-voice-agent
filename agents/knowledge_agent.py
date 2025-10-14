# agents/knowledge_agent.py

"""
Knowledge Agent - RAG Style retrieval from dummy KB using FAISS and OpenAI Embeddings
Supports English, Kannada and mixed language queries
"""

import faiss
import numpy as np
import logging
from typing import List
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

DUMMY_KB_TEXT = """
ಕರ್ನಾಟಕ ಅರಣ್ಯ ಇಲಾಖೆ | KARNATAKA FOREST DEPARTMENT
ಸಂಪರ್ಕಿಸಿ/Contact: etimberkfd@gmail.com
ಅಧಿಸೂಚನೆ ಮತ್ತು ಲಾಟ್‌ ವಿವರ/ Notification & LOT Details
ಇಲಾಖಾ ಲಾಗಿನ್ / Dept Login
ಮಾಸಿಕ ಕ್ಯಾಲೆಂಡರ್ | Month calendar
ವಾರ್ಷಿಕ ಕ್ಯಾಲೆಂಡರ್ | Yearly calendar
ಕಡೆಯ ನಾಟಾ ಹರಾಜಿನ ವಿವರ | Last Timber Auction Details

ವೃತ್ತ Circle: Dharwad | ವಿಭಾಗ Division: Haveri
ಡಿಪೋ Depot: Tadas | ಹರಾಜು ದಿನಾಂಕ Auction Date: 03-09-2025
ಮಾರಾಟವಾದ ಲಾಟ್‌ಗಳು Sold lots: 112 | ಮಾರಾಟವಾಗದ ಲಾಟ್‌ಗಳು UnSold lots: 4
ಒಟ್ಟು ಲಾಟ್‌ಗಳ ಸಂಖ್ಯೆ Total No of Lots: 33 | ಒಟ್ಟು ಮೊತ್ತ Total Bid Amt: 16110479.52

ಹರಾಜು ದಿನಾಂಕ Auction Date | Depot Name | View Details
03-09-2025 | Tadas
03-09-2025 | Hirekrur
03-09-2025 | Gangajalam Tenkey
02-09-2025 | Kalbetta
02-09-2025 | Vajra Nursery Tenky

ಅತಿಥಿಗಳ ಸಂಖ್ಯೆ No of Visitors: 1,406,818
© 2025 ಕರ್ನಾಟಕ ಅರಣ್ಯ ಇಲಾಖೆ | Karnataka Forest Department | ಸೃಜನೆ ಮತ್ತು ಅಭಿವೃದ್ದಿ: ಮಾಸಂತಂ ಕೇಂದ್ರ Designed and Developed by ICT Centre
"""

class KnowledgeAgent(BaseAgent):
    """
    Conversational agent for dynamic knowledge retrieval (RAG-Style)
    using a FAISS vector store of website text.
    """
    
    def __init__(self, kb_text: str = DUMMY_KB_TEXT):
        super().__init__(
            instructions=(
                "You are a helpful assistant for Karnataka Government website info. "
                "Answer users based on the retrieved website text. "
                "Respond concisely in the same language as the user's query."
            ),
            llm=openai.LLM(model="gpt-4o-mini", parallel_tool_calls=False)
        )
        self.kb_text = kb_text
        self.chunks = self._chunk_text(kb_text)
        self.index, self.embeddings = None, None

    async def build_index(self):
        """Build FAISS index asynchronously (call once at startup)."""
        embeddings = []
        for chunk in self.chunks:
            emb = await openai.embedding(
                model="text-embedding-3-small",
                input=chunk
            )
            embeddings.append(np.array(emb.data[0].embedding, dtype=np.float32))
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.stack(embeddings))
        self.index, self.embeddings = index, embeddings
        logger.info("FAISS index built with %d chunks", len(self.chunks))

    def _chunk_text(self, text: str, chunk_size: int = 300) -> List[str]:
        sentences = text.split("\n")
        chunks, current = [], ""
        for s in sentences:
            if len(current.split()) + len(s.split()) <= chunk_size:
                current += " " + s
            else:
                chunks.append(current.strip())
                current = s
        if current:
            chunks.append(current.strip())
        return chunks
    
    async def _retrieve_chunks(self, query: str, top_k=3) -> List[str]:
        if self.index is None:
            await self.build_index()

        emb = await openai.embedding(
            model="text-embedding-3-small",
            input=query
        )
        query_vec = np.array(emb.data[0].embedding, dtype=np.float32).reshape(1, -1)
        D, I = self.index.search(query_vec, top_k)
        return [self.chunks[i] for i in I[0]]
    
    @function_tool()
    async def answer_query(self, user_query: str) -> str:
        """
        Handle a user query by retrieving relevant text chunks and
        generating a concise answer using the LLM.
        """
        relevant_texts = await self._retrieve_chunks(user_query)
        context = "\n".join(relevant_texts)
        
        prompt = (
            f"You are a helpful assistant. Answer the following question based on the context below:\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {user_query}\n"
            f"Answer concisely in the same language as the question."
        )
        response = await self.chat(prompt)
        return response
