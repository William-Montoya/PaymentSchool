import {
  X,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import type {
  PrecioCarrera,
} from '../../types/precio'

import type {
  InscripcionFinanzas,
  ObligacionCreateAction,
  ObligacionCreateMode,
  TipoObligacionManual,
} from '../../types/obligacion'


interface Props {
  mode: ObligacionCreateMode

  inscripcion:
    InscripcionFinanzas

  precios:
    PrecioCarrera[]

  pricesLoading: boolean
  catalogError: string | null

  isSubmitting: boolean
  error: string | null

  onClose: () => void

  onSubmit: (
    action:
      ObligacionCreateAction,
  ) => Promise<void>
}


const manualLabels:
Record<
  TipoObligacionManual,
  string
> = {
  INSCRIPCION:
    'Inscripción',

  CERTIFICACION:
    'Certificación',

  CONSTANCIA:
    'Constancia',

  OTRO:
    'Otro',
}


function nullable(
  value: string,
): string | null {
  const normalized =
    value.trim()

  return normalized
    ? normalized
    : null
}


function formatMoney(
  value: string,
) {
  return (
    new Intl.NumberFormat(
      'es-GT',
      {
        style: 'currency',
        currency: 'GTQ',
      },
    )
    .format(
      Number(value),
    )
  )
}


function ObligacionFormModal({
  mode,
  inscripcion,
  precios,
  pricesLoading,
  catalogError,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const [
    idPrecio,
    setIdPrecio,
  ] = useState('')

  const [
    fechaVencimiento,
    setFechaVencimiento,
  ] = useState('')

  const [
    fechaInicio,
    setFechaInicio,
  ] = useState('')

  const [
    cantidadMeses,
    setCantidadMeses,
  ] = useState('1')

  const [
    concepto,
    setConcepto,
  ] = useState('')

  const [
    tipoManual,
    setTipoManual,
  ] = useState<
    TipoObligacionManual
  >('OTRO')

  const [
    periodo,
    setPeriodo,
  ] = useState('')

  const [
    fechaManual,
    setFechaManual,
  ] = useState('')

  const [
    monto,
    setMonto,
  ] = useState('')

  const preciosDisponibles =
    useMemo(
      () =>
        precios.filter(
          (precio) => {
            if (
              mode ===
              'MENSUALIDADES'
            ) {
              return (
                precio.tipo ===
                'MENSUALIDAD'
              )
            }

            return (
              precio.tipo !==
              'MENSUALIDAD'
            )
          },
        ),
      [
        mode,
        precios,
      ],
    )

  const precioSeleccionado =
    preciosDisponibles.find(
      (precio) =>
        precio.id_precio ===
        Number(idPrecio),
    ) ?? null

  const title =
    mode === 'DESDE_PRECIO'
      ? 'Generar desde tarifa'
      : mode ===
          'MENSUALIDADES'
        ? 'Generar mensualidades'
        : 'Crear obligación manual'

  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (
      mode === 'DESDE_PRECIO'
    ) {
      if (
        !idPrecio ||
        !fechaVencimiento
      ) {
        return
      }

      await onSubmit({
        mode:
          'DESDE_PRECIO',

        payload: {
          id_inscripcion:
            inscripcion
              .id_inscripcion,

          id_precio:
            Number(idPrecio),

          fecha_vencimiento:
            fechaVencimiento,
        },
      })

      return
    }

    if (
      mode === 'MENSUALIDADES'
    ) {
      if (
        !idPrecio ||
        !fechaInicio
      ) {
        return
      }

      await onSubmit({
        mode:
          'MENSUALIDADES',

        payload: {
          id_inscripcion:
            inscripcion
              .id_inscripcion,

          id_precio:
            Number(idPrecio),

          fecha_inicio:
            fechaInicio,

          cantidad_meses:
            Number(
              cantidadMeses,
            ),
        },
      })

      return
    }

    if (
      !concepto.trim() ||
      !monto
    ) {
      return
    }

    await onSubmit({
      mode: 'MANUAL',

      payload: {
        id_inscripcion:
          inscripcion
            .id_inscripcion,

        concepto:
          concepto.trim(),

        tipo_obligacion:
          tipoManual,

        periodo:
          nullable(
            periodo,
          ),

        fecha_vencimiento:
          nullable(
            fechaManual,
          ),

        monto_bruto:
          monto,
      },
    })
  }

  const disablePriceSubmit =
    (
      mode !== 'MANUAL' &&
      (
        pricesLoading ||
        !idPrecio
      )
    )

  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <section
        className="student-modal finance-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="obligacion-modal-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Finanzas
            </span>

            <h2 id="obligacion-modal-title">
              {title}
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            aria-label="Cerrar"
            disabled={
              isSubmitting
            }
            onClick={onClose}
          >
            <X
              size={19}
              aria-hidden="true"
            />
          </button>
        </header>

        <form
          className="student-form"
          onSubmit={handleSubmit}
        >
          <div className="finance-inscription-context">
            <div>
              <span>
                Estudiante
              </span>

              <strong>
                {inscripcion.estudiante}
              </strong>

              <small>
                {
                  inscripcion
                    .codigo_estudiante
                }
              </small>
            </div>

            <div>
              <span>
                Ciclo
              </span>

              <strong>
                {inscripcion.ciclo}
              </strong>
            </div>

            <div>
              <span>
                Oferta
              </span>

              <strong>
                {inscripcion.carrera}
              </strong>

              <small>
                {inscripcion.grado}
              </small>
            </div>
          </div>

          {mode !== 'MANUAL' && (
            <div className="student-form-grid">
              <div className="form-field student-form-full">
                <label htmlFor="precio">
                  Tarifa *
                </label>

                <select
                  id="precio"
                  value={idPrecio}
                  disabled={
                    pricesLoading
                  }
                  required
                  onChange={(event) =>
                    setIdPrecio(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    {pricesLoading
                      ? 'Cargando tarifas...'
                      : 'Selecciona una tarifa'}
                  </option>

                  {preciosDisponibles.map(
                    (precio) => (
                      <option
                        key={
                          precio.id_precio
                        }
                        value={
                          precio.id_precio
                        }
                      >
                        {precio.concepto}
                        {' — '}
                        {formatMoney(
                          precio.monto,
                        )}
                      </option>
                    ),
                  )}
                </select>
              </div>

              {precioSeleccionado && (
                <div className="finance-price-preview student-form-full">
                  <div>
                    <span>
                      Concepto
                    </span>

                    <strong>
                      {
                        precioSeleccionado
                          .concepto
                      }
                    </strong>
                  </div>

                  <div>
                    <span>
                      Monto
                    </span>

                    <strong>
                      {formatMoney(
                        precioSeleccionado
                          .monto,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Vigencia
                    </span>

                    <strong>
                      {
                        precioSeleccionado
                          .fecha_inicio
                      }
                      {' → '}
                      {
                        precioSeleccionado
                          .fecha_fin ??
                        'Sin fecha final'
                      }
                    </strong>
                  </div>
                </div>
              )}

              {mode ===
                'DESDE_PRECIO' && (
                <div className="form-field student-form-full">
                  <label htmlFor="fecha-vencimiento">
                    Fecha de vencimiento *
                  </label>

                  <input
                    id="fecha-vencimiento"
                    type="date"
                    required
                    value={
                      fechaVencimiento
                    }
                    onChange={(event) =>
                      setFechaVencimiento(
                        event.target.value,
                      )
                    }
                  />
                </div>
              )}

              {mode ===
                'MENSUALIDADES' && (
                <>
                  <div className="form-field">
                    <label htmlFor="fecha-inicio">
                      Fecha inicial *
                    </label>

                    <input
                      id="fecha-inicio"
                      type="date"
                      required
                      value={
                        fechaInicio
                      }
                      onChange={(event) =>
                        setFechaInicio(
                          event.target.value,
                        )
                      }
                    />
                  </div>

                  <div className="form-field">
                    <label htmlFor="cantidad-meses">
                      Cantidad de meses *
                    </label>

                    <input
                      id="cantidad-meses"
                      type="number"
                      min={1}
                      max={24}
                      required
                      value={
                        cantidadMeses
                      }
                      onChange={(event) =>
                        setCantidadMeses(
                          event.target.value,
                        )
                      }
                    />
                  </div>
                </>
              )}
            </div>
          )}

          {mode === 'MANUAL' && (
            <div className="student-form-grid">
              <div className="form-field student-form-full">
                <label htmlFor="concepto">
                  Concepto *
                </label>

                <input
                  id="concepto"
                  value={concepto}
                  maxLength={150}
                  required
                  onChange={(event) =>
                    setConcepto(
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="tipo-obligacion">
                  Tipo *
                </label>

                <select
                  id="tipo-obligacion"
                  value={tipoManual}
                  onChange={(event) =>
                    setTipoManual(
                      event.target
                        .value as
                        TipoObligacionManual,
                    )
                  }
                >
                  {(
                    Object.entries(
                      manualLabels,
                    ) as [
                      TipoObligacionManual,
                      string,
                    ][]
                  ).map(
                    ([
                      value,
                      label,
                    ]) => (
                      <option
                        key={value}
                        value={value}
                      >
                        {label}
                      </option>
                    ),
                  )}
                </select>
              </div>

              <div className="form-field">
                <label htmlFor="periodo">
                  Período
                </label>

                <input
                  id="periodo"
                  value={periodo}
                  maxLength={20}
                  placeholder="Ej. 2026-10"
                  onChange={(event) =>
                    setPeriodo(
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="fecha-manual">
                  Fecha de vencimiento
                </label>

                <input
                  id="fecha-manual"
                  type="date"
                  value={fechaManual}
                  onChange={(event) =>
                    setFechaManual(
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="monto-bruto">
                  Monto *
                </label>

                <input
                  id="monto-bruto"
                  type="number"
                  min="0"
                  step="0.01"
                  required
                  value={monto}
                  onChange={(event) =>
                    setMonto(
                      event.target.value,
                    )
                  }
                />
              </div>
            </div>
          )}

          {catalogError &&
            mode !== 'MANUAL' && (
              <div className="form-error">
                {catalogError}
              </div>
            )}

          {!pricesLoading &&
            mode !== 'MANUAL' &&
            preciosDisponibles.length ===
              0 &&
            !catalogError && (
              <div className="finance-warning-box">
                No hay tarifas activas
                disponibles para esta
                carrera, grado y tipo de
                operación.
              </div>
            )}

          {error && (
            <div
              className="form-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <footer className="student-modal-actions">
            <button
              className="button button-secondary"
              type="button"
              disabled={
                isSubmitting
              }
              onClick={onClose}
            >
              Cancelar
            </button>

            <button
              className="button button-primary"
              type="submit"
              disabled={
                isSubmitting ||
                disablePriceSubmit
              }
            >
              {isSubmitting
                ? 'Procesando...'
                : mode ===
                    'MENSUALIDADES'
                  ? 'Generar mensualidades'
                  : 'Crear obligación'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}


export default ObligacionFormModal