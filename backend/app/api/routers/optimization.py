from fastapi import APIRouter, Depends

from app.api.dependencies import get_csv_repository, get_optimizer_service
from app.repositories.csv_repository import CSVRepository
from app.schemas.optimization import OptimizationRequest, OptimizationResponse
from app.services.optimizer_service import OptimizerService

router = APIRouter(prefix="/optimizer", tags=["Optimizer"])


@router.post("/recommendation", response_model=OptimizationResponse)
def create_recommendation(
    payload: OptimizationRequest,
    csv_repository: CSVRepository = Depends(get_csv_repository),
    optimizer_service: OptimizerService = Depends(get_optimizer_service),
) -> OptimizationResponse:
    experiments_df, metadata_df = csv_repository.load(payload.dataset_prefix)
    return optimizer_service.optimize(payload, experiments_df, metadata_df)
