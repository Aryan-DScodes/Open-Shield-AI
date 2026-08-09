import json
import numpy as np
import redis.asyncio as redis
from redis.commands.search.query import Query
from typing import Optional, Dict, Any
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType

class SemanticCache:
    def __init__(self, redis_client: redis.Redis, threshold: float = 0.92):
        self.redis = redis_client
        self.threshold = threshold
        self.index_name = "prompt_cache_idx"
        self.distance_threshold = 1.0 - threshold  # Convert similarity to Cosine distance

    async def _get_embedding(self, text: str) -> np.ndarray:
        # INSTRUCTION FOR AI CODER: Replace with actual embedding generation 
        # (e.g., via sentence-transformers, ONNX, or upstream Embeddings API).
        # Returning a dummy 384-dimensional vector for boilerplate.
        return np.random.rand(384).astype(np.float32)

    
    async def check_cache(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Searches Redis using Vector Similarity Search (KNN).
        Returns the cached LLM response if similarity > threshold.
        """
        try:
            query_vector = await self._get_embedding(prompt)
            vector_bytes = query_vector.tobytes()

            # Query: Find top 1 nearest neighbor using Cosine distance
            q = (
                Query("*=>[KNN 1 @embedding $vec_param AS vector_score]")
                .sort_by("vector_score")
                .return_fields("response", "vector_score")
                .paging(0, 1)
                .dialect(2)
            )
            
            params = {"vec_param": vector_bytes}
            res = await self.redis.ft(self.index_name).search(q, params)

            if res.docs:
                best_match = res.docs[0]
                distance = float(best_match.vector_score)
                
                if distance <= self.distance_threshold:
                    return json.loads(best_match.response)
                    
            return None
            
        except Exception as e:
            # Fallback to cache miss if index is missing/error occurs
            return None

    async def store_cache(self, prompt: str, response: dict) -> None:
        """
        Stores the prompt embedding and upstream response in Redis as a HASH.
        """
        prompt_id = hash(prompt)
        query_vector = await self._get_embedding(prompt)
        
        mapping = {
            "prompt": prompt,
            "response": json.dumps(response),
            "embedding": query_vector.tobytes()
        }
        
        await self.redis.hset(f"cache:{prompt_id}", mapping=mapping)
        # Set TTL to 24 hours to prevent stale cache buildup
        await self.redis.expire(f"cache:{prompt_id}", 86400)
    async def init_index(self):
    #Creates the RediSearch Vector Index if it does not exist.
        try:
            await self.redis.ft(self.index_name).info()
        except Exception:
            # Index does not exist, create it
            schema = (
                TextField("prompt"),
                TextField("response"),
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": 384,
                        "DISTANCE_METRIC": "COSINE"
                    }
                )
            )
            definition = IndexDefinition(prefix=["cache:"], index_type=IndexType.HASH)
            await self.redis.ft(self.index_name).create_index(fields=schema, definition=definition)