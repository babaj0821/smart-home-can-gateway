import json
import os

from copy import deepcopy
from threading import RLock


class ScenarioStorage:

    def __init__(
        self,
        path=None
    ):

        if path is None:

            base_dir = os.path.dirname(
                os.path.abspath(
                    __file__
                )
            )

            path = os.path.join(
                base_dir,
                "scenario_data.json"
            )


        self.path = path

        self._lock = RLock()

        self._ensure_file()


    def _ensure_file(
        self
    ):

        directory = os.path.dirname(
            self.path
        )


        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        if (
            not os.path.exists(
                self.path
            )
            or
            os.path.getsize(
                self.path
            ) == 0
        ):

            self._write(
                {
                    "scenarios": {}
                }
            )


    def _read(
        self
    ):

        with self._lock:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:

                raw = file.read()


            if not raw.strip():

                return {
                    "scenarios": {}
                }


            data = json.loads(
                raw
            )


            if not isinstance(
                data,
                dict
            ):

                raise ValueError(
                    "Scenario database root must be an object"
                )


            scenarios = data.get(
                "scenarios"
            )


            if not isinstance(
                scenarios,
                dict
            ):

                raise ValueError(
                    "Scenario database must contain a scenarios object"
                )


            return data


    def _write(
        self,
        data
    ):

        with self._lock:

            temp_path = (
                self.path
                +
                ".tmp"
            )


            with open(
                temp_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )


                file.flush()


                os.fsync(
                    file.fileno()
                )


            os.replace(
                temp_path,
                self.path
            )


    def create(
        self,
        name,
        scenario
    ):

        with self._lock:

            data = self._read()


            if name in data[
                "scenarios"
            ]:

                raise ValueError(
                    f"Scenario already exists: {name}"
                )


            data[
                "scenarios"
            ][name] = deepcopy(
                scenario
            )


            self._write(
                data
            )


    def get(
        self,
        name
    ):

        data = self._read()


        scenario = data[
            "scenarios"
        ].get(
            name
        )


        if scenario is None:

            return None


        return deepcopy(
            scenario
        )


    def get_all(
        self
    ):

        data = self._read()


        return deepcopy(
            data[
                "scenarios"
            ]
        )


    def update(
        self,
        old_name,
        new_name,
        scenario
    ):

        with self._lock:

            data = self._read()


            scenarios = data[
                "scenarios"
            ]


            if old_name not in scenarios:

                raise ValueError(
                    f"Scenario not found: {old_name}"
                )


            if (
                new_name != old_name
                and
                new_name in scenarios
            ):

                raise ValueError(
                    f"Scenario already exists: {new_name}"
                )


            if new_name != old_name:

                del scenarios[
                    old_name
                ]


            scenarios[
                new_name
            ] = deepcopy(
                scenario
            )


            self._write(
                data
            )


    def delete(
        self,
        name
    ):

        with self._lock:

            data = self._read()


            if name not in data[
                "scenarios"
            ]:

                raise ValueError(
                    f"Scenario not found: {name}"
                )


            del data[
                "scenarios"
            ][name]


            self._write(
                data
            )


            return True
