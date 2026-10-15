# RutaNorte_Logistics
Caso 02 - RutaNorte Logistics. Diseño Arquitectural del Sistema

## Equipo 2
| Matrícula | Nombre |
|-----------|--------|
| 2049234 | Basurto Rivera Ramsés Tenosh |
| 2050864 | Cerda Herrera Juan Kristof |
| 2066053 | Esparza Torres Carlos Arturo |

## Empresa
RutaNorte Logistics es una empresa de transporte de mercancía que opera entre Monterrey, Saltillo, Reynosa, San Luis Potosí y Querétaro. Necesita digitalizar el seguimiento de cada orden de servicio de principio a fin: que los operadores dejen de comunicarse por WhatsApp, que las fases queden registradas en tiempo real y que las evidencias de entrega estén organizadas por folio.

## Alcance
Propuesta de arquitectura de la capa de lógica de negocio

- Patrón de lógica de negocio elegido: **Domain Model** (comparado contra Transaction Script y Table Module).
- Mapa de dominio (entidades, value objects, aggregates, domain services y domain events).
- Service Layer, Repository, Unit of Work y CQRS básico.
- Revisión con los principios SOLID.
- 3 ADR (decisiones de arquitectura).
- Cinco casos de uso: CU-01 Solicitar y confirmar cotización, CU-02 Generar orden y asignar unidad, CU-03 Registrar entrega con evidencia, CU-04 Cancelar o devolver una orden, CU-05 Reasignar unidad por avería.
- Código base en Python que representa la arquitectura (no es una aplicación completa).

Fuera de alcance: interfaz de usuario, base de datos real, tiempos por fase, rechazo de asignación por el operador y alertas a Ventas y Operaciones al cancelar sin unidad

