import {
  MessageCircle,
  Printer,
  X,
} from 'lucide-react'

import type {
  InscripcionFinanzas,
  ObligacionSaldo,
} from '../../types/obligacion'

import type {
  ComprobantePagoResponse,
} from '../../types/pago'

import {
  printPagoReceipt,
  type ReceiptStudentInfo,
} from '../../utils/printPagoReceipt'

interface Props {
  comprobante: ComprobantePagoResponse
  estudiante: ReceiptStudentInfo
  inscripciones: InscripcionFinanzas[]
  obligaciones: Record<number, ObligacionSaldo>
  whatsappNumber: string | null
  whatsappContactName: string | null
  onClose: () => void
}

function formatMoney(
  value: string | number,
): string {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ',
  }).format(Number(value))
}

function formatDateTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-GT', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function normalizeWhatsappNumber(
  value: string,
): string | null {
  let digits = value.replace(/\D/g, '')

  if (!digits) {
    return null
  }

  if (digits.length === 8) {
    digits = `502${digits}`
  }

  if (digits.startsWith('00')) {
    digits = digits.slice(2)
  }

  return digits.length >= 10
    ? digits
    : null
}

function ReceiptModal({
  comprobante,
  estudiante,
  inscripciones,
  obligaciones,
  whatsappNumber,
  whatsappContactName,
  onClose,
}: Props) {
  const recibo = comprobante.recibo

  function handlePrint() {
    if (!recibo) {
      return
    }

    printPagoReceipt({
      estudiante,
      inscripciones,
      comprobante,
      obligaciones,
    })
  }

  function handleWhatsapp() {
    if (!recibo || !whatsappNumber) {
      return
    }

    const normalized = normalizeWhatsappNumber(whatsappNumber)

    if (!normalized) {
      window.alert(
        'El número de WhatsApp registrado no tiene un formato válido.',
      )
      return
    }

    const message = [
      `Buen día${whatsappContactName ? ` ${whatsappContactName}` : ''}.`,
      '',
      `Se registró un pago de ${estudiante.nombre}.`,
      `Recibo: ${recibo.numero_recibo}`,
      `Monto: ${formatMoney(comprobante.pago.monto_total)}`,
      `Fecha: ${formatDateTime(comprobante.pago.fecha_pago)}`,
      '',
      'Puede solicitar o adjuntar el comprobante PDF desde PaymentSchool.',
    ].join('\n')

    window.open(
      `https://wa.me/${normalized}?text=${encodeURIComponent(message)}`,
      '_blank',
      'noopener,noreferrer',
    )
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section
        className="student-modal payment-receipt-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="payment-receipt-title"
      >
        <header className="student-modal-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Pagos
            </span>

            <h2 id="payment-receipt-title">
              {recibo?.numero_recibo ?? 'Comprobante de pago'}
            </h2>
          </div>

          <button
            className="modal-close"
            type="button"
            aria-label="Cerrar"
            onClick={onClose}
          >
            <X size={19} aria-hidden="true" />
          </button>
        </header>

        <div className="payment-receipt-body">
          <section className="payment-receipt-preview">
            <div className="payment-receipt-preview-top">
              <div>
                <span className="dashboard-card-eyebrow">
                  PaymentSchool
                </span>
                <h3>Comprobante oficial de pago</h3>
                <p>
                  La impresión se genera en formato A4 con Original y
                  Copia en la misma hoja.
                </p>
              </div>

              <div className="payment-receipt-number">
                <span>Recibo</span>
                <strong>{recibo?.numero_recibo ?? 'Pendiente'}</strong>
              </div>
            </div>

            <div className="payment-receipt-summary-grid">
              <article>
                <span>Estudiante</span>
                <strong>{estudiante.nombre}</strong>
                <small>{estudiante.codigo}</small>
              </article>

              <article>
                <span>Fecha</span>
                <strong>{formatDateTime(comprobante.pago.fecha_pago)}</strong>
                <small>{comprobante.pago.metodo}</small>
              </article>

              <article>
                <span>Total recibido</span>
                <strong>{formatMoney(comprobante.pago.monto_total)}</strong>
                <small>{comprobante.pago.estado}</small>
              </article>
            </div>

            <div className="module-table-wrapper payment-receipt-table">
              <table className="module-table">
                <thead>
                  <tr>
                    <th>Concepto</th>
                    <th>Período</th>
                    <th>Aplicado</th>
                    <th>Saldo actual</th>
                  </tr>
                </thead>

                <tbody>
                  {comprobante.aplicaciones.map((aplicacion) => (
                    <tr key={aplicacion.id_aplicacion}>
                      <td>
                        <strong>{aplicacion.concepto}</strong>
                        <div className="finance-table-secondary">
                          {aplicacion.tipo_obligacion}
                        </div>
                      </td>

                      <td>{aplicacion.periodo ?? '—'}</td>

                      <td>
                        {formatMoney(aplicacion.monto_aplicado)}
                      </td>

                      <td>
                        <strong>
                          {obligaciones[aplicacion.id_obligacion]
                            ? formatMoney(
                                obligaciones[aplicacion.id_obligacion].saldo,
                              )
                            : '—'}
                        </strong>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {recibo && (
              <div className="payment-verification-box">
                <span>Código de verificación</span>
                <strong>{recibo.codigo_verificacion}</strong>
              </div>
            )}
          </section>

          {!recibo && (
            <div className="finance-warning-box">
              Este pago aún no tiene recibo asociado. No puede imprimirse
              hasta generar el recibo.
            </div>
          )}

          {recibo && !whatsappNumber && (
            <div className="finance-info-box">
              No hay un número de WhatsApp disponible para el contacto
              principal, o tu usuario no tiene permiso para consultarlo.
            </div>
          )}
        </div>

        <footer className="student-modal-actions payment-receipt-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={onClose}
          >
            Cerrar
          </button>

          <button
            className="button button-secondary"
            type="button"
            disabled={!recibo || !whatsappNumber}
            onClick={handleWhatsapp}
          >
            <MessageCircle size={16} aria-hidden="true" />
            WhatsApp
          </button>

          <button
            className="button button-primary"
            type="button"
            disabled={!recibo}
            onClick={handlePrint}
          >
            <Printer size={16} aria-hidden="true" />
            Imprimir / PDF
          </button>
        </footer>
      </section>
    </div>
  )
}

export default ReceiptModal
