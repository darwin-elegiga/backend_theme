#!/bin/bash
# Script para probar los endpoints de la API de temas

BASE_URL="${1:-http://localhost:8000}"

echo "=== Testing Theme Backend API ==="
echo "Base URL: $BASE_URL"
echo ""

# Health check
echo "1. Health Check"
echo "   GET /api/health"
curl -s "$BASE_URL/api/health" | python3 -m json.tool
echo ""

# Listar brands
echo "2. List Brands"
echo "   GET /api/brands"
curl -s "$BASE_URL/api/brands" | python3 -m json.tool
echo ""

# Obtener tema de Mapfre
echo "3. Get Mapfre Theme"
echo "   GET /api/theme/mapfre"
curl -s "$BASE_URL/api/theme/mapfre" | python3 -m json.tool
echo ""

# Obtener CSS de fuentes
echo "4. Get Mapfre Fonts CSS"
echo "   GET /api/fonts/mapfre/fonts.css"
curl -s "$BASE_URL/api/fonts/mapfre/fonts.css"
echo ""
echo ""

# Probar brand inexistente (404)
echo "5. Test 404 - Non-existent brand"
echo "   GET /api/theme/nonexistent"
curl -s -w "\n   HTTP Status: %{http_code}\n" "$BASE_URL/api/theme/nonexistent" | head -20
echo ""

echo "=== Tests completed ==="
