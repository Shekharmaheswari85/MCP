from typing import Dict, Any, List, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class QueryType(Enum):
    PRODUCT = "product"
    CATEGORY = "category"
    BRAND = "brand"
    SEARCH = "search"
    GENERAL = "general"

@dataclass
class QueryAnalysis:
    query_type: QueryType
    confidence: float
    entities: List[str]
    suggested_providers: List[str]
    required_fields: List[str]

class QueryAnalyzer:
    """Analyzes queries to determine the best provider and required fields"""
    
    def __init__(self):
        self.provider_weights = {
            "database": 1.0,
            "graphql": 0.8,
            "rest": 0.6
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze the query to determine its type and required information"""
        query = query.lower()
        
        # Determine query type
        query_type = self._determine_query_type(query)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Determine required fields
        required_fields = self._determine_required_fields(query_type, entities)
        
        # Determine suggested providers
        suggested_providers = self._determine_providers(query_type, entities)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_type, entities)
        
        return QueryAnalysis(
            query_type=query_type,
            confidence=confidence,
            entities=entities,
            suggested_providers=suggested_providers,
            required_fields=required_fields
        )
    
    def _determine_query_type(self, query: str) -> QueryType:
        """Determine the type of query"""
        query = query.lower()
        
        if any(word in query for word in ["product", "item", "phone", "laptop", "device"]):
            return QueryType.PRODUCT
        elif any(word in query for word in ["category", "type", "kind"]):
            return QueryType.CATEGORY
        elif any(word in query for word in ["brand", "manufacturer", "company"]):
            return QueryType.BRAND
        elif any(word in query for word in ["search", "find", "look for"]):
            return QueryType.SEARCH
        else:
            return QueryType.GENERAL
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract relevant entities from the query"""
        entities = []
        query = query.lower()
        
        # Common product-related terms
        product_terms = ["iphone", "samsung", "laptop", "phone", "tablet", "watch"]
        for term in product_terms:
            if term in query:
                entities.append(term)
        
        # Common category terms
        category_terms = ["electronics", "phones", "computers", "accessories"]
        for term in category_terms:
            if term in query:
                entities.append(term)
        
        # Common brand terms
        brand_terms = ["apple", "samsung", "google", "microsoft"]
        for term in brand_terms:
            if term in query:
                entities.append(term)
        
        return entities
    
    def _determine_required_fields(self, query_type: QueryType, entities: List[str]) -> List[str]:
        """Determine which fields are required based on query type and entities"""
        base_fields = ["id", "name", "description"]
        
        if query_type == QueryType.PRODUCT:
            return base_fields + ["price", "specifications", "in_stock"]
        elif query_type == QueryType.CATEGORY:
            return base_fields + ["products"]
        elif query_type == QueryType.BRAND:
            return base_fields + ["products", "categories"]
        elif query_type == QueryType.SEARCH:
            return base_fields + ["price", "category", "brand"]
        else:
            return base_fields
    
    def _determine_providers(self, query_type: QueryType, entities: List[str]) -> List[str]:
        """Determine which providers to try based on query type and entities"""
        providers = []
        
        # Always try database first
        providers.append("database")
        
        # Add GraphQL for complex queries
        if query_type in [QueryType.PRODUCT, QueryType.SEARCH]:
            providers.append("graphql")
        
        # Add REST for simple queries
        if query_type in [QueryType.CATEGORY, QueryType.BRAND]:
            providers.append("rest")
        
        return providers
    
    def _calculate_confidence(self, query_type: QueryType, entities: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = 0.5
        
        # Increase confidence based on query type
        if query_type != QueryType.GENERAL:
            base_confidence += 0.2
        
        # Increase confidence based on number of entities
        if entities:
            base_confidence += min(len(entities) * 0.1, 0.3)
        
        return min(base_confidence, 1.0) 