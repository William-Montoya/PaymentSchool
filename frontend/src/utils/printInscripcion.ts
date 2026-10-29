import type {
  Contacto,
} from '../types/contacto'

import type {
  Estudiante,
} from '../types/estudiante'

import type {
  InscripcionDetalle,
  TipoInscripcion,
} from '../types/inscripcion'


interface PrintData {
  inscripcion:
    InscripcionDetalle

  estudiante:
    Estudiante |
    null

  contactoPrincipal:
    Contacto |
    null
}


const tipoLabels:
Record<TipoInscripcion, string> = {
  NUEVA:
    'Nueva inscripción',

  REINSCRIPCION:
    'Reinscripción',

  TRASLADO:
    'Traslado',
}


function escapeHtml(
  value:
    string |
    number |
    null |
    undefined,
): string {
  const text =
    value === null ||
    value === undefined
      ? ''
      : String(value)

  return text
    .replaceAll(
      '&',
      '&amp;',
    )
    .replaceAll(
      '<',
      '&lt;',
    )
    .replaceAll(
      '>',
      '&gt;',
    )
    .replaceAll(
      '"',
      '&quot;',
    )
    .replaceAll(
      "'",
      '&#039;',
    )
}


function formatDate(
  value:
    string |
    null |
    undefined,
): string {
  if (!value) {
    return '—'
  }

  const [
    year,
    month,
    day,
  ] = value.split('-')

  if (
    !year ||
    !month ||
    !day
  ) {
    return value
  }

  return `${day}/${month}/${year}`
}


function valueOrDash(
  value:
    string |
    null |
    undefined,
): string {
  return value?.trim()
    ? value
    : '—'
}


export function printInscripcionComprobante({
  inscripcion,
  estudiante,
  contactoPrincipal,
}: PrintData) {
  const printWindow =
    window.open(
      '',
      '_blank',
      'width=900,height=760',
    )

  if (!printWindow) {
    return
  }

  const numeroComprobante =
    `INS-${String(
      inscripcion.id_inscripcion,
    ).padStart(6, '0')}`

  const nombreEstudiante =
    estudiante
      ? (
        `${estudiante.nombres} ` +
        estudiante.apellidos
      )
      : inscripcion.estudiante

  const html = `
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>
  Comprobante de inscripción ${escapeHtml(
    numeroComprobante,
  )}
</title>

<style>
  * {
    box-sizing: border-box;
  }

  @page {
    size: A4;
    margin: 14mm;
  }

  body {
    margin: 0;
    background: #ffffff;
    color: #182033;
    font-family:
      Arial,
      Helvetica,
      sans-serif;
    font-size: 12px;
  }

  .document {
    width: 100%;
    max-width: 190mm;
    margin: 0 auto;
    border: 1px solid #d9dce5;
  }

  .header {
    padding: 22px 28px;
    border-bottom: 3px solid #7657e8;
    text-align: center;
  }

  .brand {
    margin: 0 0 5px;
    color: #7657e8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  h1 {
    margin: 0;
    color: #182033;
    font-size: 22px;
    letter-spacing: .4px;
  }

  .subtitle {
    margin: 7px 0 0;
    color: #687087;
  }

  .meta {
    display: grid;
    grid-template-columns:
      repeat(3, 1fr);
    border-bottom: 1px solid #d9dce5;
    background: #f7f8fb;
  }

  .meta div {
    padding: 12px 16px;
    border-right: 1px solid #d9dce5;
  }

  .meta div:last-child {
    border-right: 0;
  }

  .label {
    display: block;
    margin-bottom: 4px;
    color: #7d8496;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .6px;
    text-transform: uppercase;
  }

  .value {
    color: #182033;
    font-weight: 700;
  }

  .section {
    padding: 18px 28px;
    border-bottom: 1px solid #e3e5eb;
  }

  .section-title {
    margin: 0 0 14px;
    color: #7657e8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .8px;
    text-transform: uppercase;
  }

  .grid {
    display: grid;
    grid-template-columns:
      repeat(2, 1fr);
    gap: 14px 28px;
  }

  .field {
    min-height: 42px;
  }

  .full {
    grid-column: 1 / -1;
  }

  .observations {
    min-height: 55px;
    padding: 10px 12px;
    border: 1px solid #e0e2e8;
    background: #fafbfc;
    white-space: pre-wrap;
  }

  .statement {
    padding: 20px 28px;
    color: #4e566b;
    line-height: 1.65;
    text-align: justify;
  }

  .signatures {
    display: grid;
    grid-template-columns:
      repeat(2, 1fr);
    gap: 50px;
    padding: 42px 28px 24px;
  }

  .signature {
    padding-top: 7px;
    border-top: 1px solid #596174;
    text-align: center;
  }

  .signature small {
    display: block;
    margin-top: 5px;
    color: #7b8294;
  }

  .footer {
    padding: 12px 28px;
    background: #f7f8fb;
    color: #8b91a1;
    font-size: 9px;
    text-align: center;
  }

  @media print {
    .document {
      border: 0;
    }
  }
</style>
</head>

<body>
  <article class="document">

    <header class="header">
      <p class="brand">
        PaymentSchool
      </p>

      <h1>
        COMPROBANTE DE INSCRIPCIÓN
      </h1>

      <p class="subtitle">
        Constancia de registro académico
      </p>
    </header>

    <section class="meta">
      <div>
        <span class="label">
          No. comprobante
        </span>

        <span class="value">
          ${escapeHtml(
            numeroComprobante,
          )}
        </span>
      </div>

      <div>
        <span class="label">
          Fecha de inscripción
        </span>

        <span class="value">
          ${escapeHtml(
            formatDate(
              inscripcion
                .fecha_inscripcion,
            ),
          )}
        </span>
      </div>

      <div>
        <span class="label">
          Estado
        </span>

        <span class="value">
          ${escapeHtml(
            inscripcion.estado,
          )}
        </span>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">
        Datos del estudiante
      </h2>

      <div class="grid">
        <div class="field">
          <span class="label">
            Código / Carnet
          </span>

          <span class="value">
            ${escapeHtml(
              inscripcion
                .codigo_estudiante,
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Estudiante
          </span>

          <span class="value">
            ${escapeHtml(
              nombreEstudiante,
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            CUI
          </span>

          <span class="value">
            ${escapeHtml(
              valueOrDash(
                estudiante?.cui,
              ),
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Fecha de nacimiento
          </span>

          <span class="value">
            ${escapeHtml(
              formatDate(
                estudiante
                  ?.fecha_nacimiento,
              ),
            )}
          </span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">
        Datos académicos
      </h2>

      <div class="grid">
        <div class="field">
          <span class="label">
            Ciclo escolar
          </span>

          <span class="value">
            ${escapeHtml(
              inscripcion.ciclo,
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Carrera
          </span>

          <span class="value">
            ${escapeHtml(
              inscripcion.carrera,
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Grado
          </span>

          <span class="value">
            ${escapeHtml(
              inscripcion.grado,
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Tipo de inscripción
          </span>

          <span class="value">
            ${escapeHtml(
              tipoLabels[
                inscripcion.tipo
              ],
            )}
          </span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">
        Contacto principal
      </h2>

      <div class="grid">
        <div class="field">
          <span class="label">
            Nombre
          </span>

          <span class="value">
            ${escapeHtml(
              valueOrDash(
                contactoPrincipal
                  ?.nombre,
              ),
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Parentesco
          </span>

          <span class="value">
            ${escapeHtml(
              valueOrDash(
                contactoPrincipal
                  ?.parentesco,
              ),
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            Teléfono
          </span>

          <span class="value">
            ${escapeHtml(
              valueOrDash(
                contactoPrincipal
                  ?.telefono,
              ),
            )}
          </span>
        </div>

        <div class="field">
          <span class="label">
            WhatsApp
          </span>

          <span class="value">
            ${escapeHtml(
              valueOrDash(
                contactoPrincipal
                  ?.whatsapp,
              ),
            )}
          </span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">
        Observaciones
      </h2>

      <div class="observations">
        ${escapeHtml(
          valueOrDash(
            inscripcion.observaciones,
          ),
        )}
      </div>
    </section>

    <section class="statement">
      El presente documento hace constar
      que el estudiante indicado ha sido
      registrado en el ciclo académico y
      oferta académica señalados en este
      comprobante.
    </section>

    <section class="signatures">
      <div class="signature">
        Firma de administración

        <small>
          Firma y sello
        </small>
      </div>

      <div class="signature">
        Firma del encargado

        <small>
          Recibido
        </small>
      </div>
    </section>

    <footer class="footer">
      Documento generado por PaymentSchool
    </footer>

  </article>

<script>
  window.addEventListener(
    'load',
    function () {
      window.focus()

      setTimeout(
        function () {
          window.print()
        },
        250
      )
    }
  )
</script>
</body>
</html>
`

  printWindow.document.open()
  printWindow.document.write(
    html,
  )
  printWindow.document.close()
}