#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

# Kolory do czytelnego wyjścia
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local data=$4

    if [ -z "$data" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    if [ "$status" -eq "$expected_status" ]; then
        echo -e "[$method $endpoint] Expected: $expected_status | Got: $status -> ${GREEN}OK${NC}"
    else
        echo -e "[$method $endpoint] Expected: $expected_status | Got: $status -> ${RED}FAIL${NC}"
    fi
}

echo "=== TESTOWANIE KONTRAKTU API ==="

# GET /projects
check_endpoint "GET" "/projects" 200

# POST /projects (Sukces i 409)
check_endpoint "POST" "/projects" 201 '{"name": "Nowy Projekt"}'
check_endpoint "POST" "/projects" 409 '{"name": "TaskBoard"}'

# GET /projects/{id}
check_endpoint "GET" "/projects/1" 200
check_endpoint "GET" "/projects/999" 404

# GET /users
check_endpoint "GET" "/users" 200
check_endpoint "GET" "/users/1" 200
check_endpoint "GET" "/users/999" 404

# POST /tasks walidacje
check_endpoint "POST" "/tasks" 201 '{"project_id": 1, "title": "Testowe zadanie"}'
check_endpoint "POST" "/tasks" 422 '{"project_id": 1, "title": "  "}'
check_endpoint "POST" "/tasks" 422 '{"project_id": 999, "title": "Nieistniejący projekt"}'

# GET /tasks/{id} i DELETE
check_endpoint "GET" "/tasks/999" 404
check_endpoint "DELETE" "/tasks/999" 404

echo "=== ZAKOŃCZONO ==="