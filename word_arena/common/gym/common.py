from pydantic import BaseModel


class TrainingConfig(BaseModel):
    num_train_loops: int
    num_in_loop_trials: int
    seed: int
