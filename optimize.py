import argparse
import logging

from constants import SEED
from utils import (
    add_historical_trials,
    get_data_from_path,
    get_distributions,
    get_formatted_parameter,
    get_objective,
    parse_experiments,
    visualize,
)

logging.getLogger("optuna").setLevel(logging.WARNING)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", help="Input prefix for files PREFIX.data.csv and PREFIX.meta.csv.")
    parser.add_argument("--best", "-b", help="Return only the historical best trial.", action="store_true")
    parser.add_argument("--persons", "-p", help="Consider only scores of a set of persons.", nargs="+")
    parser.add_argument(
        "--method",
        "-m",
        help="Scoring method.",
        default="median",
        choices=("mean", "median", "lowest", "highest"),
    )
    parser.add_argument(
        "--weight",
        "-w",
        help="Weight of the prior in optimization.",
        type=float,
        default=0.666,
    )
    parser.add_argument("--time", "-t", help="Show optimization history.", action="store_true")
    parser.add_argument("--relations", "-r", help="Show parameter relations.", action="store_true")
    parser.add_argument("--edf", "-e", help="Show empirical distribution function.", action="store_true")
    parser.add_argument("--importance", "-i", help="Show parameter importance.", action="store_true")
    parser.add_argument("--slice", "-s", help="Show how parameters influence the objective.", action="store_true")
    parser.add_argument("--scores", "-S", help="Show distribution of scores per person.", action="store_true")
    return parser


def main() -> None:
    import optuna

    args = build_parser().parse_args()

    experiments_df, metadata_df = get_data_from_path(args.input)
    historical_experiments_df, fixed_parameters, unique_category_dict = parse_experiments(
        experiments_df, metadata_df, args.persons, args.method
    )
    distributions = get_distributions(metadata_df, unique_category_dict)

    sampler = optuna.samplers.TPESampler(
        n_startup_trials=0,
        seed=SEED,
        prior_weight=args.weight,
    )
    study = optuna.create_study(
        sampler=sampler,
        direction="maximize",
        study_name="Coffee Optimization",
    )
    add_historical_trials(study, distributions, historical_experiments_df)

    visualize(study, experiments_df, metadata_df, args)

    if args.best:
        next_parameters = study.best_params
        best_value = study.best_value
        print(f"Showing best parameters, with a score of {best_value}")
    else:
        objective = get_objective(distributions, fixed_parameters)
        study.optimize(objective, n_trials=1)
        next_parameters = study.trials[-1].params

    for parameter, value in fixed_parameters.items():
        print(get_formatted_parameter(parameter, value, metadata_df, fixed=True))
    for parameter, value in next_parameters.items():
        print(get_formatted_parameter(parameter, value, metadata_df))


if __name__ == "__main__":
    main()
