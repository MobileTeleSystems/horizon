Role Permissions
================

Horizon implements a role-based access control model to manage permissions across different entities in the service.

Role Model Overview
-------------------

In Horizon, roles are defined within the context of namespaces, with the exception of the superadmin role. A user can be associated with one, several, or no namespaces at all.

- **GUEST**: User without a specific namespace assignment, having limited access rights.
- **DEVELOPER**: Users with development-related permissions.
- **MAINTAINER**: Users with permissions similar to developers but with additional rights in certain areas.
- **OWNER**: Users with full permissions within their owned namespaces and associated HWMs.
- **SUPERADMIN**: Users with full system-wide permissions.

Namespace Permissions
---------------------

.. list-table::
    :header-rows: 1
    :widths: 20 10 10 10 10 10

    * - Role
      - Create
      - Read
      - Update
      - Delete
      - Manage Users
    * - GUEST
      - ``+``
      - ``+``
      - ``-``
      - ``-``
      - ``-``
    * - DEVELOPER
      - ``+``
      - ``+``
      - ``-``
      - ``-``
      - ``-``
    * - MAINTAINER
      - ``+``
      - ``+``
      - ``-``
      - ``-``
      - ``-``
    * - OWNER
      - ``+``
      - ``+``
      - ``+``
      - ``+``
      - ``+``
    * - SUPERADMIN
      - ``+``
      - ``+``
      - ``+``
      - ``+``
      - ``+``


HWM Permissions
---------------

.. list-table::
    :header-rows: 1
    :widths: 20 10 10 10 10

    * - Role
      - Create
      - Read
      - Update
      - Delete
    * - GUEST
      - ``-``
      - ``+``
      - ``-``
      - ``-``
    * - DEVELOPER
      - ``+``
      - ``+``
      - ``+``
      - ``-``
    * - MAINTAINER
      - ``+``
      - ``+``
      - ``+``
      - ``+``
    * - OWNER
      - ``+``
      - ``+``
      - ``+``
      - ``+``
    * - SUPERADMIN
      - ``+``
      - ``+``
      - ``+``
      - ``+``


Relation Between Namespaces and HWMs
-------------------------------------

Each High Water Mark (HWM) is associated with a namespace in a many-to-one relationship, meaning a single namespace can have multiple HWMs associated with it. The role assigned to a user within a namespace indirectly dictates their permissions over the HWMs associated with that namespace.

Architecture Diagram with Permissions
-------------------------------------

.. plantuml::

    @startuml
    title Permissions Model

    skinparam linetype polyline
    left to right direction
    skinparam rectangle {
        BackgroundColor<<no_role>> Wheat
        BackgroundColor<<developer>> LightGreen
        BackgroundColor<<maintainer>> LightBlue
        BackgroundColor<<owner>> Gold
    }

    actor "User" as User
    rectangle "Permissions" {
        (Namespace) as Namespace
        (HWM) as HWM
    }

    User --> Namespace : Assigned Roles
    Namespace --> HWM : "Manages"

    Namespace -right-> Roles : Defines Role

    note right of Roles : Roles define the\npermissions within\nnamespaces and HWMs.
    @enduml
