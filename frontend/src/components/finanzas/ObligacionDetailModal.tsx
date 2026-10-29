import {
  X,
} from 'lucide-react'

import type {
  ObligacionSaldo,
  TipoObligacion,
} from '../../types/obligacion'


interface Props {
  obligacion:
    ObligacionSaldo

  onClose: () => void
}


const tipoLabels:
Record<TipoObligacion, string> = {
  INSCRIPCION:
    'Inscripción',

  MENSUALIDAD:
    'Mensualidad',

  CERTIFICACION:
    'Certificación',

  CONSTANCIA:
    'Constancia',

  OTRO:
    'Otro',
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


function formatDate(
  value:
    string |
    null,
) {
  if (!value) {
    return 'Sin fecha'
  }

  return new Intl
    .DateTimeFormat(
      'es-GT',
      {
        dateStyle: 'medium',
      },
    )
    .format(
      new Date(
        `${value}T00:00:00`,
      ),
    )
}


function ObligacionDetailModal({
  obligacion,
  onClose,
}: Props) {
  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <section
        className="student-modal finance-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="obligacion-detail-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Finanzas
            </span>

            <h2 id="obligacion-detail-title">
              Detalle de obligación
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X
              size={19}
              aria-hidden="true"
            />
          </button>
        </header>

        <div className="finance-detail-body">
          <div className="finance-detail-heading">
            <div>
              <span>
                Obligación
              </span>

              <strong>
                #
                {
                  obligacion
                    .id_obligacion
                }
              </strong>
            </div>

            <div>
              <span>
                Estado
              </span>

              <strong>
                {obligacion.estado}
              </strong>
            </div>
          </div>

          <div className="finance-detail-grid">
            <article>
              <span>
                Concepto
              </span>

              <strong>
                {obligacion.concepto}
              </strong>
            </article>

            <article>
              <span>
                Tipo
              </span>

              <strong>
                {
                  tipoLabels[
                    obligacion
                      .tipo_obligacion
                  ]
                }
              </strong>
            </article>

            <article>
              <span>
                Período
              </span>

              <strong>
                {
                  obligacion
                    .periodo ??
                  'No aplica'
                }
              </strong>
            </article>

            <article>
              <span>
                Vencimiento
              </span>

              <strong>
                {formatDate(
                  obligacion
                    .fecha_vencimiento,
                )}
              </strong>
            </article>

            <article>
              <span>
                Monto bruto
              </span>

              <strong>
                {formatMoney(
                  obligacion
                    .monto_bruto,
                )}
              </strong>
            </article>

            <article>
              <span>
                Descuentos
              </span>

              <strong>
                {formatMoney(
                  obligacion
                    .monto_descuento,
                )}
              </strong>
            </article>

            <article>
              <span>
                Beca
              </span>

              <strong>
                {formatMoney(
                  obligacion
                    .monto_beca,
                )}
              </strong>
            </article>

            <article>
              <span>
                Monto neto
              </span>

              <strong>
                {formatMoney(
                  obligacion
                    .monto_neto,
                )}
              </strong>
            </article>

            <article>
              <span>
                Total pagado
              </span>

              <strong>
                {formatMoney(
                  obligacion
                    .total_pagado,
                )}
              </strong>
            </article>

            <article className="finance-detail-balance">
              <span>
                Saldo pendiente
              </span>

              <strong>
                {formatMoney(
                  obligacion.saldo,
                )}
              </strong>
            </article>
          </div>
        </div>

        <footer className="student-modal-actions">
          <button
            className="button button-primary"
            type="button"
            onClick={onClose}
          >
            Cerrar
          </button>
        </footer>
      </section>
    </div>
  )
}


export default ObligacionDetailModal