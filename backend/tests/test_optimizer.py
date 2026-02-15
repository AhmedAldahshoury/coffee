from fastapi.testclient import TestClient

from app.main import app


def test_recommendation_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/optimizer/recommendation',
        json={
            'dataset_prefix': 'aeropress.',
            'method': 'median',
            'best_only': True,
            'prior_weight': 0.666,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert 'suggested_parameters' in payload
    assert isinstance(payload['suggested_parameters'], list)
