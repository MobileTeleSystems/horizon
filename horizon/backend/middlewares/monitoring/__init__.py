# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from horizon.backend.middlewares.monitoring.metrics import (
    apply_monitoring_metrics_middleware,
)
from horizon.backend.middlewares.monitoring.stats import (
    apply_monitoring_stats_middleware,
)

__all__ = [
    "apply_monitoring_metrics_middleware",
    "apply_monitoring_stats_middleware",
]
