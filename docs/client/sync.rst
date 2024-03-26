.. _client-sync:

Sync client
===========

Quickstart
----------

Here is a short example of using sync client to interact with backend.

Create client object:

>>> from horizon.client.sync import HorizonClientSync
>>> from horizon.client.auth import LoginPassword
>>> client = HorizonClientSync(
...     base_url="http://some.domain.com/api",
...     auth=LoginPassword(login="me", password="12345"),
... )

Check for credentials and issue access token:

>>> client.authorize()

Create namespace with name "my_namespace":

>>> from horizon.commons.schemas.v1 import NamespaceCreateRequestV1
>>> created_namespace = client.create_namespace(NamespaceCreateRequestV1(name="my_namespace"))
>>> created_namespace
NamespaceResponseV1(
    id=1,
    name="my_namespace",
    description="",
)

Create HWM with name "my_hwm" in this namespace:

>>> from horizon.commons.schemas.v1 import HWMCreateRequestV1
>>> hwm = HWMCreateRequestV1(
...     namespace_id=created_namespace.id,
...     name="my_hwm",
...     type="column_int",
...     value=123,
... )
>>> created_hwm = client.create_hwm(hwm)
>>> created_hwm
HWMResponseV1(
    id=1,
    namespace_id=1,
    name="my_hwm",
    description="",
    type="column_int",
    value=123,
    entity="",
    expression="",
)

Update HWM with name "my_hwm" in this namespace:

>>> from horizon.commons.schemas.v1 import HWMUpdateRequestV1
>>> hwm_change = HWMUpdateRequestV1(value=234)
>>> updated_hwm = client.update_hwm(created_hwm.id, hwm_change)
>>> updated_hwm
HWMResponseV1(
    id=1,
    namespace_id=1,
    name="my_hwm",
    description="",
    type="column_int",
    value=234,
    entity="",
    expression="",
)

Reference
---------

.. currentmodule:: horizon.client.sync

.. autoclass:: HorizonClientSync
    :members: authorize, ping, whoami, paginate_namespaces, get_namespace, create_namespace, update_namespace, delete_namespace, paginate_hwm, get_hwm, create_hwm, update_hwm, delete_hwm, bulk_delete_hwm, get_namespace_permissions, update_namespace_permissions, paginate_hwm_history, paginate_namespace_history, retry, copy_hwms
    :member-order: bysource

.. autoclass:: RetryConfig
    :members: no

.. autoclass:: TimeoutConfig
    :members: no
