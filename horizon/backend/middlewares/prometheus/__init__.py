# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from horizon.backend.middlewares.prometheus.metrics import (
    add_prometheus_metrics_middleware,
)
from horizon.backend.middlewares.prometheus.stats import add_prometheus_stats_middleware
