import pytest
import json
from index import app

@pytest.fixture
def client():
    """Configura o app Flask para testes."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Testa o endpoint de health check."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

def test_buscar_com_frase_existente(client):
    """Testa a busca por uma frase que sabemos que existe."""
    response = client.post('/api/buscar', json={'frase': 'raindrops'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    # Verifica se a primeira música encontrada é a esperada
    assert data[0]['musica'] == 'raindrops (an angel cried)'
    assert '<strong>raindrops</strong>' in data[0]['estrofe']
    # Testa o novo campo de referência ABNT
    assert 'referencia_abnt' in data[0]
    assert 'GRANDE, Ariana.' in data[0]['referencia_abnt']
    assert 'RAINDROPS (AN ANGEL CRIED)' in data[0]['referencia_abnt']
    # Assumindo que o álbum 'Sweetener' está no CSV para esta música
    assert '<strong>Sweetener</strong>' in data[0]['referencia_abnt']

def test_buscar_com_frase_inexistente(client):
    """Testa a busca por uma frase que não deve retornar resultados."""
    response = client.post('/api/buscar', json={'frase': 'xyz_nao_existe_123'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_buscar_sem_frase(client):
    """Testa o comportamento quando a frase é vazia."""
    response = client.post('/api/buscar', json={'frase': '   '})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_buscar_com_payload_invalido(client):
    """Testa o endpoint com um JSON malformado (sem o campo 'frase')."""
    response = client.post('/api/buscar', json={'texto': 'invalido'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'erro' in data
    assert "O campo 'frase' é obrigatório" in data['detalhes']

def test_buscar_thank_u_next(client):
    """
    Testa a busca por uma frase com pontuação e que sabemos que existe.
    Este teste é crucial para depurar o problema atual.
    """
    response = client.post('/api/buscar', json={'frase': 'thank u, next'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Esperamos que encontre pelo menos um resultado
    assert len(data) > 0, "A busca por 'thank u, next' não retornou resultados."
    # Verifica se a música correta foi encontrada
    assert data[0]['musica'].lower() == 'thank u, next'
    assert '<strong>thank u, next</strong>' in data[0]['estrofe']
    assert '<strong>Thank U, Next</strong>' in data[0]['referencia_abnt']
