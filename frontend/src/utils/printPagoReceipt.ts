import type {
  InscripcionFinanzas,
  ObligacionSaldo,
} from '../types/obligacion'

import type {
  ComprobantePagoResponse,
} from '../types/pago'

export interface ReceiptStudentInfo {
  codigo: string
  nombre: string
  cui: string | null
}

export interface PrintPagoReceiptData {
  estudiante: ReceiptStudentInfo
  inscripciones: InscripcionFinanzas[]
  comprobante: ComprobantePagoResponse
  obligaciones: Record<number, ObligacionSaldo>
}

function escapeHtml(
  value: string | number | null | undefined,
): string {
  const text = value === null || value === undefined
    ? ''
    : String(value)

  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
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

function formatPeriod(periodo: string | null): string {
  if (!periodo) {
    return '—'
  }

  const match = /^(\d{4})-(\d{2})$/.exec(periodo)

  if (!match) {
    return periodo
  }

  const date = new Date(
    Number(match[1]),
    Number(match[2]) - 1,
    1,
  )

  const month = new Intl.DateTimeFormat('es-GT', {
    month: 'long',
  }).format(date)

  return `${month.charAt(0).toUpperCase()}${month.slice(1)} ${match[1]}`
}

function getAcademicContext(
  data: PrintPagoReceiptData,
): string {
  const idsInscripcion = new Set<number>()

  for (const aplicacion of data.comprobante.aplicaciones) {
    const obligacion = data.obligaciones[aplicacion.id_obligacion]

    if (obligacion) {
      idsInscripcion.add(obligacion.id_inscripcion)
    }
  }

  const contexts = data.inscripciones.filter((inscripcion) =>
    idsInscripcion.has(inscripcion.id_inscripcion),
  )

  if (contexts.length === 0) {
    const fallback = data.inscripciones[0]

    if (!fallback) {
      return 'Sin contexto académico disponible'
    }

    return `${fallback.ciclo} · ${fallback.carrera} · ${fallback.grado}`
  }

  return contexts
    .map(
      (inscripcion) =>
        `${inscripcion.ciclo} · ${inscripcion.carrera} · ${inscripcion.grado}`,
    )
    .join(' / ')
}

function renderCopy(
  label: 'ORIGINAL' | 'COPIA',
  data: PrintPagoReceiptData,
): string {
  const { comprobante } = data
  const recibo = comprobante.recibo

  const rows = comprobante.aplicaciones
    .map((aplicacion) => {
      const obligacion = data.obligaciones[aplicacion.id_obligacion]
      const saldo = obligacion?.saldo ?? null

      return `
        <tr>
          <td>${escapeHtml(aplicacion.concepto)}</td>
          <td>${escapeHtml(formatPeriod(aplicacion.periodo))}</td>
          <td>${escapeHtml(aplicacion.tipo_obligacion)}</td>
          <td class="money">${escapeHtml(formatMoney(aplicacion.monto_aplicado))}</td>
          <td class="money">${saldo === null ? '—' : escapeHtml(formatMoney(saldo))}</td>
        </tr>
      `
    })
    .join('')

  return `
    <section class="receipt-copy">
      <div class="copy-label">${label}</div>

      <header class="receipt-header">
        <div>
          <div class="brand">PaymentSchool</div>
          <h1>COMPROBANTE OFICIAL DE PAGO</h1>
          <p>Control académico y financiero</p>
        </div>

        <div class="receipt-number">
          <span>RECIBO</span>
          <strong>${escapeHtml(recibo?.numero_recibo ?? 'SIN RECIBO')}</strong>
          <small>${escapeHtml(comprobante.pago.estado)}</small>
        </div>
      </header>

      <div class="info-grid">
        <div>
          <span class="label">Estudiante</span>
          <strong>${escapeHtml(data.estudiante.nombre)}</strong>
        </div>

        <div>
          <span class="label">Código / Carnet</span>
          <strong>${escapeHtml(data.estudiante.codigo)}</strong>
        </div>

        <div>
          <span class="label">CUI</span>
          <strong>${escapeHtml(data.estudiante.cui || '—')}</strong>
        </div>

        <div>
          <span class="label">Fecha de pago</span>
          <strong>${escapeHtml(formatDateTime(comprobante.pago.fecha_pago))}</strong>
        </div>

        <div class="full">
          <span class="label">Contexto académico</span>
          <strong>${escapeHtml(getAcademicContext(data))}</strong>
        </div>

        <div>
          <span class="label">Método</span>
          <strong>${escapeHtml(comprobante.pago.metodo)}</strong>
        </div>

        <div>
          <span class="label">Referencia</span>
          <strong>${escapeHtml(comprobante.pago.referencia || '—')}</strong>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Concepto</th>
            <th>Período</th>
            <th>Tipo</th>
            <th class="money">Aplicado</th>
            <th class="money">Saldo actual</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>

      <div class="totals">
        <div>
          <span>Total recibido</span>
          <strong>${escapeHtml(formatMoney(comprobante.pago.monto_total))}</strong>
        </div>

        <div>
          <span>Total aplicado</span>
          <strong>${escapeHtml(formatMoney(comprobante.pago.total_aplicado))}</strong>
        </div>
      </div>

      <div class="receipt-footer-grid">
        <div>
          <span class="label">Código de verificación</span>
          <strong class="verification">${escapeHtml(recibo?.codigo_verificacion ?? '—')}</strong>
        </div>

        <div class="signature">
          Firma / sello
        </div>
      </div>

      <footer>
        Documento generado por PaymentSchool
      </footer>
    </section>
  `
}

export function printPagoReceipt(
  data: PrintPagoReceiptData,
): void {
  const printWindow = window.open(
    '',
    '_blank',
    'width=980,height=900',
  )

  if (!printWindow) {
    return
  }

  const html = `
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>${escapeHtml(data.comprobante.recibo?.numero_recibo ?? 'Recibo de pago')}</title>
<style>
  * { box-sizing: border-box; }

  @page {
    size: A4 portrait;
    margin: 8mm;
  }

  body {
    margin: 0;
    background: #ffffff;
    color: #172033;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9px;
  }

  .sheet {
    width: 100%;
    max-width: 194mm;
    margin: 0 auto;
  }

  .receipt-copy {
    position: relative;
    min-height: 132mm;
    padding: 7mm;
    border: 1px solid #dfe3eb;
    border-radius: 2mm;
    overflow: hidden;
  }

  .copy-label {
    position: absolute;
    top: 5mm;
    right: 6mm;
    padding: 1.5mm 3mm;
    border: 1px solid #7c4dff;
    border-radius: 999px;
    color: #6d3df1;
    font-size: 7px;
    font-weight: 700;
    letter-spacing: .9px;
  }

  .receipt-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 4mm;
    border-bottom: 2px solid #7c4dff;
    gap: 8mm;
  }

  .brand {
    color: #7c4dff;
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }

  h1 {
    margin: 1.5mm 0 1mm;
    font-size: 15px;
  }

  .receipt-header p {
    margin: 0;
    color: #6f778b;
  }

  .receipt-number {
    display: grid;
    min-width: 48mm;
    padding-top: 8mm;
    text-align: right;
  }

  .receipt-number span,
  .label {
    color: #7d8597;
    font-size: 6.5px;
    font-weight: 700;
    letter-spacing: .5px;
    text-transform: uppercase;
  }

  .receipt-number strong {
    margin-top: 1mm;
    font-size: 11px;
  }

  .receipt-number small {
    margin-top: .8mm;
    color: #24865e;
    font-weight: 700;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 3mm 5mm;
    padding: 4mm 0;
  }

  .info-grid > div {
    display: grid;
    gap: 1mm;
  }

  .info-grid .full {
    grid-column: span 2;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th {
    padding: 2.2mm;
    background: #f4f5f8;
    color: #6f778b;
    font-size: 6.5px;
    text-align: left;
    text-transform: uppercase;
  }

  td {
    padding: 2.2mm;
    border-bottom: 1px solid #e6e8ed;
    vertical-align: top;
  }

  .money {
    text-align: right;
    white-space: nowrap;
  }

  .totals {
    display: flex;
    justify-content: flex-end;
    gap: 7mm;
    padding: 3.5mm 0 2mm;
  }

  .totals > div {
    display: grid;
    min-width: 31mm;
    gap: .8mm;
    text-align: right;
  }

  .totals span {
    color: #7d8597;
    font-size: 7px;
  }

  .totals strong {
    font-size: 12px;
  }

  .receipt-footer-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    align-items: end;
    gap: 10mm;
    margin-top: 3mm;
  }

  .verification {
    display: block;
    margin-top: 1mm;
    font-size: 7px;
    overflow-wrap: anywhere;
  }

  .signature {
    padding-top: 4mm;
    border-top: 1px solid #5d6575;
    text-align: center;
  }

  footer {
    margin-top: 3mm;
    color: #959bab;
    font-size: 6.5px;
    text-align: center;
  }

  .cut-line {
    display: flex;
    align-items: center;
    height: 9mm;
    gap: 3mm;
    color: #8c93a2;
    font-size: 8px;
  }

  .cut-line::before,
  .cut-line::after {
    content: '';
    flex: 1;
    border-top: 1px dashed #8c93a2;
  }

  @media print {
    .receipt-copy {
      border-color: #bfc5d0;
    }
  }
</style>
</head>
<body>
  <main class="sheet">
    ${renderCopy('ORIGINAL', data)}
    <div class="cut-line">✂</div>
    ${renderCopy('COPIA', data)}
  </main>

  <script>
    window.addEventListener('load', function () {
      window.focus();
      setTimeout(function () { window.print(); }, 250);
    });
  </script>
</body>
</html>
  `

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
}
