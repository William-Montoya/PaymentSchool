import {
  CalendarDays,
  Database,
  Eye,
  FileClock,
  Filter,
  RotateCcw,
  UserRound,
  X,
} from 'lucide-react'

import {
  useState,
  type FormEvent,
} from 'react'

import {
  useQuery,
} from '@tanstack/react-query'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  getAuditoria,
  getAuditoriaCatalogos,
  getAuditorias,
} from '../api/auditoria'

import type {
  AuditoriaRegistro,
} from '../types/auditoria'

import '../styles/audit.css'


const PAGE_SIZE = 50


interface AuditFilters {
  idUsuario: string
  modulo: string
  accion: string
  tabla: string
  idRegistro: string
  fechaDesde: string
  fechaHasta: string
}


const emptyFilters: AuditFilters = {
  idUsuario: '',
  modulo: '',
  accion: '',
  tabla: '',
  idRegistro: '',
  fechaDesde: '',
  fechaHasta: '',
}


function formatDateTime(
  value: string,
) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      dateStyle: 'short',
      timeStyle: 'medium',
    },
  ).format(date)
}


function humanize(
  value: string | null,
) {
  if (!value) {
    return '—'
  }

  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(
      /(^|\s)\S/g,
      (character) =>
        character.toUpperCase(),
    )
}


function JsonPanel({
  title,
  data,
}: {
  title: string
  data: Record<string, unknown> | null
}) {
  return (
    <section className="audit-json-panel">
      <h3>{title}</h3>

      {data ? (
        <pre>
          {JSON.stringify(
            data,
            null,
            2,
          )}
        </pre>
      ) : (
        <p>
          Sin información registrada.
        </p>
      )}
    </section>
  )
}


function AuditDetailModal({
  idAuditoria,
  onClose,
}: {
  idAuditoria: number
  onClose: () => void
}) {
  const detailQuery = useQuery({
    queryKey: [
      'auditoria-detalle',
      idAuditoria,
    ],
    queryFn: () =>
      getAuditoria(idAuditoria),
  })

  return (
    <div
      className="audit-modal-backdrop"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="audit-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-detail-title"
        onMouseDown={(event) =>
          event.stopPropagation()
        }
      >
        <header className="audit-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Auditoría
            </span>

            <h2 id="audit-detail-title">
              Evento #{idAuditoria}
            </h2>
          </div>

          <button
            className="audit-close-button"
            type="button"
            aria-label="Cerrar detalle"
            onClick={onClose}
          >
            <X
              size={18}
              aria-hidden="true"
            />
          </button>
        </header>

        {detailQuery.isLoading ? (
          <div className="module-message">
            Cargando detalle...
          </div>
        ) : detailQuery.isError ||
          !detailQuery.data ? (
          <div className="module-message module-message-error">
            {getApiErrorMessage(
              detailQuery.error,
              'No fue posible cargar el evento de auditoría.',
            )}
          </div>
        ) : (
          <AuditDetailContent
            audit={detailQuery.data}
          />
        )}
      </section>
    </div>
  )
}


function AuditDetailContent({
  audit,
}: {
  audit: AuditoriaRegistro
}) {
  return (
    <div className="audit-modal-content">
      <section className="audit-detail-grid">
        <div>
          <span>Fecha y hora</span>
          <strong>
            {formatDateTime(
              audit.fecha_evento,
            )}
          </strong>
        </div>

        <div>
          <span>Usuario</span>
          <strong>
            {audit.username ??
              'Sistema'}
          </strong>
        </div>

        <div>
          <span>Módulo</span>
          <strong>
            {humanize(audit.modulo)}
          </strong>
        </div>

        <div>
          <span>Acción</span>
          <strong>
            {humanize(audit.accion)}
          </strong>
        </div>

        <div>
          <span>Tabla</span>
          <strong>
            {audit.tabla_afectada ??
              '—'}
          </strong>
        </div>

        <div>
          <span>ID registro</span>
          <strong>
            {audit.id_registro ??
              '—'}
          </strong>
        </div>

        <div>
          <span>Dirección IP</span>
          <strong>
            {audit.ip ?? '—'}
          </strong>
        </div>

        <div>
          <span>ID usuario</span>
          <strong>
            {audit.id_usuario ??
              '—'}
          </strong>
        </div>
      </section>

      <section className="audit-description">
        <span>Descripción</span>
        <p>
          {audit.descripcion ||
            'Sin descripción.'}
        </p>
      </section>

      <div className="audit-json-grid">
        <JsonPanel
          title="Datos anteriores"
          data={
            audit.datos_anteriores
          }
        />

        <JsonPanel
          title="Datos nuevos"
          data={audit.datos_nuevos}
        />
      </div>
    </div>
  )
}


function AuditPage() {
  const [draft, setDraft] =
    useState<AuditFilters>(
      emptyFilters,
    )

  const [filters, setFilters] =
    useState<AuditFilters>(
      emptyFilters,
    )

  const [offset, setOffset] =
    useState(0)

  const [selectedAuditId, setSelectedAuditId] =
    useState<number | null>(null)

  const [filterError, setFilterError] =
    useState<string | null>(null)

  const catalogQuery = useQuery({
    queryKey: [
      'auditoria-catalogos',
    ],
    queryFn: getAuditoriaCatalogos,
  })

  const auditQuery = useQuery({
    queryKey: [
      'auditoria-lista',
      filters,
      offset,
    ],
    queryFn: () =>
      getAuditorias({
        id_usuario:
          filters.idUsuario
            ? Number(
                filters.idUsuario,
              )
            : undefined,

        modulo:
          filters.modulo ||
          undefined,

        accion:
          filters.accion ||
          undefined,

        tabla_afectada:
          filters.tabla ||
          undefined,

        id_registro:
          filters.idRegistro
            ? Number(
                filters.idRegistro,
              )
            : undefined,

        fecha_desde:
          filters.fechaDesde
            ? `${filters.fechaDesde}T00:00:00`
            : undefined,

        fecha_hasta:
          filters.fechaHasta
            ? `${filters.fechaHasta}T23:59:59.999999`
            : undefined,

        offset,
        limit: PAGE_SIZE,
      }),
  })

  const registros =
    auditQuery.data ?? []

  const page =
    Math.floor(offset / PAGE_SIZE) + 1

  const hasNext =
    registros.length === PAGE_SIZE

  function applyFilters(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (
      draft.fechaDesde &&
      draft.fechaHasta &&
      draft.fechaDesde > draft.fechaHasta
    ) {
      setFilterError(
        'La fecha desde no puede ser posterior a la fecha hasta.',
      )
      return
    }

    setFilterError(null)
    setOffset(0)
    setFilters(draft)
  }

  function clearFilters() {
    setDraft(emptyFilters)
    setFilters(emptyFilters)
    setFilterError(null)
    setOffset(0)
  }

  const catalog =
    catalogQuery.data

  return (
    <>
      <main className="module-page audit-page">
        <header className="module-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Administración
            </span>

            <h1>Auditoría</h1>

            <p>
              Consulta cronológica de acciones,
              cambios y eventos registrados por
              el sistema.
            </p>
          </div>
        </header>

        <section className="module-card audit-filter-card">
          <header className="audit-section-header">
            <div>
              <Filter
                size={19}
                aria-hidden="true"
              />

              <div>
                <h2>Filtros</h2>
                <p>
                  Limita la bitácora por usuario,
                  módulo, acción, recurso o fecha.
                </p>
              </div>
            </div>
          </header>

          <form
            className="audit-filters"
            onSubmit={applyFilters}
          >
            <label>
              <span>Usuario</span>
              <select
                value={draft.idUsuario}
                disabled={
                  catalogQuery.isLoading
                }
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    idUsuario:
                      event.target.value,
                  }))
                }
              >
                <option value="">
                  Todos
                </option>

                {catalog?.usuarios.map(
                  (usuario) => (
                    <option
                      key={usuario.id_usuario}
                      value={usuario.id_usuario}
                    >
                      {usuario.username}
                    </option>
                  ),
                )}
              </select>
            </label>

            <label>
              <span>Módulo</span>
              <input
                list="audit-modulos"
                value={draft.modulo}
                placeholder="Todos"
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    modulo:
                      event.target.value,
                  }))
                }
              />

              <datalist id="audit-modulos">
                {catalog?.modulos.map(
                  (item) => (
                    <option
                      key={item}
                      value={item}
                    />
                  ),
                )}
              </datalist>
            </label>

            <label>
              <span>Acción</span>
              <input
                list="audit-acciones"
                value={draft.accion}
                placeholder="Todas"
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    accion:
                      event.target.value,
                  }))
                }
              />

              <datalist id="audit-acciones">
                {catalog?.acciones.map(
                  (item) => (
                    <option
                      key={item}
                      value={item}
                    />
                  ),
                )}
              </datalist>
            </label>

            <label>
              <span>Tabla</span>
              <input
                list="audit-tablas"
                value={draft.tabla}
                placeholder="Todas"
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    tabla:
                      event.target.value,
                  }))
                }
              />

              <datalist id="audit-tablas">
                {catalog?.tablas.map(
                  (item) => (
                    <option
                      key={item}
                      value={item}
                    />
                  ),
                )}
              </datalist>
            </label>

            <label>
              <span>ID registro</span>
              <input
                type="number"
                min="1"
                value={draft.idRegistro}
                placeholder="Ej. 125"
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    idRegistro:
                      event.target.value,
                  }))
                }
              />
            </label>

            <label>
              <span>Desde</span>
              <input
                type="date"
                value={draft.fechaDesde}
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    fechaDesde:
                      event.target.value,
                  }))
                }
              />
            </label>

            <label>
              <span>Hasta</span>
              <input
                type="date"
                value={draft.fechaHasta}
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    fechaHasta:
                      event.target.value,
                  }))
                }
              />
            </label>

            <div className="audit-filter-actions">
              <button
                className="button button-secondary"
                type="button"
                onClick={clearFilters}
              >
                <RotateCcw
                  size={15}
                  aria-hidden="true"
                />
                Limpiar
              </button>

              <button
                className="button button-primary"
                type="submit"
              >
                <Filter
                  size={15}
                  aria-hidden="true"
                />
                Aplicar filtros
              </button>
            </div>
          </form>

          {filterError && (
            <div className="form-error">
              {filterError}
            </div>
          )}

          {catalogQuery.isError && (
            <div className="audit-inline-warning">
              Los catálogos de filtros no pudieron
              cargarse. Los campos de texto siguen
              disponibles.
            </div>
          )}
        </section>

        <section className="audit-summary-grid">
          <article className="module-card">
            <FileClock
              size={19}
              aria-hidden="true"
            />
            <div>
              <span>Registros visibles</span>
              <strong>
                {registros.length}
              </strong>
            </div>
          </article>

          <article className="module-card">
            <UserRound
              size={19}
              aria-hidden="true"
            />
            <div>
              <span>Usuarios auditados</span>
              <strong>
                {catalog?.usuarios.length ??
                  '—'}
              </strong>
            </div>
          </article>

          <article className="module-card">
            <Database
              size={19}
              aria-hidden="true"
            />
            <div>
              <span>Módulos registrados</span>
              <strong>
                {catalog?.modulos.length ??
                  '—'}
              </strong>
            </div>
          </article>

          <article className="module-card">
            <CalendarDays
              size={19}
              aria-hidden="true"
            />
            <div>
              <span>Página</span>
              <strong>{page}</strong>
            </div>
          </article>
        </section>

        <section className="module-card">
          <header className="audit-section-header audit-list-header">
            <div>
              <FileClock
                size={19}
                aria-hidden="true"
              />

              <div>
                <h2>Bitácora de eventos</h2>
                <p>
                  Los registros más recientes se
                  muestran primero.
                </p>
              </div>
            </div>
          </header>

          {auditQuery.isLoading ? (
            <div className="module-message">
              Cargando auditoría...
            </div>
          ) : auditQuery.isError ? (
            <div className="module-message module-message-error">
              <p>
                {getApiErrorMessage(
                  auditQuery.error,
                  'No fue posible cargar la auditoría.',
                )}
              </p>

              <button
                className="button button-secondary"
                type="button"
                onClick={() => {
                  void auditQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : registros.length === 0 ? (
            <div className="audit-empty">
              <FileClock
                size={38}
                aria-hidden="true"
              />
              <strong>
                No hay eventos para los filtros
                seleccionados
              </strong>
              <p>
                Ajusta los filtros para consultar
                otros registros de auditoría.
              </p>
            </div>
          ) : (
            <div className="module-table-wrapper">
              <table className="module-table audit-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Usuario</th>
                    <th>Módulo</th>
                    <th>Acción</th>
                    <th>Recurso</th>
                    <th>Descripción</th>
                    <th>IP</th>
                    <th>Detalle</th>
                  </tr>
                </thead>

                <tbody>
                  {registros.map(
                    (audit) => (
                      <tr
                        key={
                          audit.id_auditoria
                        }
                      >
                        <td className="audit-date-cell">
                          {formatDateTime(
                            audit.fecha_evento,
                          )}
                        </td>

                        <td>
                          <strong>
                            {audit.username ??
                              'Sistema'}
                          </strong>
                          {audit.id_usuario && (
                            <div className="audit-secondary">
                              ID {audit.id_usuario}
                            </div>
                          )}
                        </td>

                        <td>
                          <span className="audit-module-badge">
                            {humanize(
                              audit.modulo,
                            )}
                          </span>
                        </td>

                        <td>
                          {humanize(
                            audit.accion,
                          )}
                        </td>

                        <td>
                          <strong>
                            {audit.tabla_afectada ??
                              '—'}
                          </strong>
                          {audit.id_registro && (
                            <div className="audit-secondary">
                              #{audit.id_registro}
                            </div>
                          )}
                        </td>

                        <td className="audit-description-cell">
                          {audit.descripcion ||
                            '—'}
                        </td>

                        <td>
                          {audit.ip ?? '—'}
                        </td>

                        <td className="table-action-column">
                          <button
                            className="table-icon-button"
                            type="button"
                            title="Ver evento"
                            aria-label="Ver evento"
                            onClick={() =>
                              setSelectedAuditId(
                                audit.id_auditoria,
                              )
                            }
                          >
                            <Eye
                              size={17}
                              aria-hidden="true"
                            />
                          </button>
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}

          <footer className="audit-pagination">
            <span>
              Página {page}
            </span>

            <div>
              <button
                className="button button-secondary"
                type="button"
                disabled={offset === 0}
                onClick={() =>
                  setOffset((current) =>
                    Math.max(
                      0,
                      current - PAGE_SIZE,
                    ),
                  )
                }
              >
                Anterior
              </button>

              <button
                className="button button-secondary"
                type="button"
                disabled={!hasNext}
                onClick={() =>
                  setOffset((current) =>
                    current + PAGE_SIZE,
                  )
                }
              >
                Siguiente
              </button>
            </div>
          </footer>
        </section>
      </main>

      {selectedAuditId !== null && (
        <AuditDetailModal
          idAuditoria={selectedAuditId}
          onClose={() =>
            setSelectedAuditId(null)
          }
        />
      )}
    </>
  )
}


export default AuditPage
