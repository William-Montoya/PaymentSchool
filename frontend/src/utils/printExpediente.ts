import type {
  Contacto,
} from '../types/contacto'

import type {
  Estudiante,
} from '../types/estudiante'

import type {
  ExpedienteDetalle,
} from '../types/expediente'


interface PrintExpedienteData {
  estudiante: Estudiante
  expediente: ExpedienteDetalle

  contactoPrincipal:
    Contacto |
    null
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


function formatDateTime(
  value: string,
): string {
  return new Intl
    .DateTimeFormat(
      'es-GT',
      {
        dateStyle:
          'medium',

        timeStyle:
          'short',
      },
    )
    .format(
      new Date(value),
    )
}


export function printExpedienteResumen({
  estudiante,
  expediente,
  contactoPrincipal,
}: PrintExpedienteData) {
  const printWindow =
    window.open(
      '',
      '_blank',
      'width=900,height=760',
    )

  if (!printWindow) {
    return
  }

  const documentos =
    expediente.documentos
      .map(
        (documento) => `
          <tr>
            <td>
              ${escapeHtml(
                documento.nombre,
              )}
            </td>

            <td>
              ${documento.obligatorio
                ? 'Sí'
                : 'No'}
            </td>

            <td>
              <strong class="${
                documento.entregado
                  ? 'ok'
                  : 'pending'
              }">
                ${documento.entregado
                  ? 'Entregado'
                  : 'Pendiente'}
              </strong>
            </td>

            <td>
              ${documento.nombre_archivo
                ? escapeHtml(
                    documento
                      .nombre_archivo,
                  )
                : 'Sin archivo'}
            </td>
          </tr>
        `,
      )
      .join('')

  const html = `
<!doctype html>
<html lang="es">

<head>
<meta charset="utf-8">

<title>
  Expediente ${escapeHtml(
    estudiante.codigo_estudiante,
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

    font-size: 11px;
  }

  .document {
    width: 100%;
    max-width: 190mm;

    margin: 0 auto;

    border:
      1px solid
      #d9dce5;
  }

  .header {
    padding:
      22px 28px;

    border-bottom:
      3px solid
      #7657e8;

    text-align: center;
  }

  .brand {
    margin:
      0 0 5px;

    color:
      #7657e8;

    font-size: 11px;
    font-weight: 700;

    letter-spacing:
      2px;

    text-transform:
      uppercase;
  }

  h1 {
    margin: 0;

    color:
      #182033;

    font-size: 21px;
  }

  .subtitle {
    margin:
      7px 0 0;

    color:
      #687087;
  }

  .status {
    display: grid;

    grid-template-columns:
      repeat(
        4,
        1fr
      );

    border-bottom:
      1px solid
      #d9dce5;

    background:
      #f7f8fb;
  }

  .status > div {
    padding:
      11px 14px;

    border-right:
      1px solid
      #d9dce5;
  }

  .status > div:last-child {
    border-right: 0;
  }

  .label {
    display: block;

    margin-bottom:
      4px;

    color:
      #7d8496;

    font-size: 8px;
    font-weight: 700;

    letter-spacing:
      .5px;

    text-transform:
      uppercase;
  }

  .value {
    color:
      #182033;

    font-weight: 700;
  }

  .section {
    padding:
      17px 28px;

    border-bottom:
      1px solid
      #e3e5eb;
  }

  .section-title {
    margin:
      0 0 12px;

    color:
      #7657e8;

    font-size: 10px;
    font-weight: 700;

    letter-spacing:
      .8px;

    text-transform:
      uppercase;
  }

  .grid {
    display: grid;

    grid-template-columns:
      repeat(
        2,
        1fr
      );

    gap:
      12px 24px;
  }

  table {
    width: 100%;

    border-collapse:
      collapse;
  }

  th,
  td {
    padding:
      8px 7px;

    border-bottom:
      1px solid
      #e5e7ed;

    text-align: left;
    vertical-align: top;
  }

  th {
    background:
      #f7f8fb;

    color:
      #687087;

    font-size: 8px;

    letter-spacing:
      .4px;

    text-transform:
      uppercase;
  }

  .ok {
    color:
      #24865e;
  }

  .pending {
    color:
      #a76906;
  }

  .observations {
    min-height: 50px;

    padding:
      10px 12px;

    border:
      1px solid
      #e1e3e8;

    background:
      #fafbfc;

    white-space:
      pre-wrap;
  }

  .signatures {
    display: grid;

    grid-template-columns:
      repeat(
        2,
        1fr
      );

    gap: 50px;

    padding:
      42px 28px
      24px;
  }

  .signature {
    padding-top: 7px;

    border-top:
      1px solid
      #596174;

    text-align: center;
  }

  .signature small {
    display: block;

    margin-top: 5px;

    color:
      #7b8294;
  }

  .footer {
    padding:
      11px 28px;

    background:
      #f7f8fb;

    color:
      #8b91a1;

    font-size: 8px;

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
      CONTROL DE EXPEDIENTE
    </h1>

    <p class="subtitle">
      Resumen de documentación del estudiante
    </p>
  </header>

  <section class="status">
    <div>
      <span class="label">
        Código / Carnet
      </span>

      <span class="value">
        ${escapeHtml(
          estudiante
            .codigo_estudiante,
        )}
      </span>
    </div>

    <div>
      <span class="label">
        Documentos requeridos
      </span>

      <span class="value">
        ${expediente
          .documentos_requeridos}
      </span>
    </div>

    <div>
      <span class="label">
        Entregados
      </span>

      <span class="value">
        ${expediente
          .documentos_entregados}
      </span>
    </div>

    <div>
      <span class="label">
        Estado
      </span>

      <span class="value">
        ${expediente.completo
          ? 'Completo'
          : 'Incompleto'}
      </span>
    </div>
  </section>

  <section class="section">
    <h2 class="section-title">
      Datos del estudiante
    </h2>

    <div class="grid">
      <div>
        <span class="label">
          Estudiante
        </span>

        <span class="value">
          ${escapeHtml(
            `${estudiante.nombres} ${estudiante.apellidos}`,
          )}
        </span>
      </div>

      <div>
        <span class="label">
          CUI
        </span>

        <span class="value">
          ${escapeHtml(
            valueOrDash(
              estudiante.cui,
            ),
          )}
        </span>
      </div>

      <div>
        <span class="label">
          Teléfono
        </span>

        <span class="value">
          ${escapeHtml(
            valueOrDash(
              estudiante.telefono,
            ),
          )}
        </span>
      </div>

      <div>
        <span class="label">
          WhatsApp
        </span>

        <span class="value">
          ${escapeHtml(
            valueOrDash(
              estudiante.whatsapp,
            ),
          )}
        </span>
      </div>
    </div>
  </section>

  <section class="section">
    <h2 class="section-title">
      Encargado principal
    </h2>

    <div class="grid">
      <div>
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

      <div>
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

      <div>
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

      <div>
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
      Control de documentos
    </h2>

    <table>
      <thead>
        <tr>
          <th>
            Documento
          </th>

          <th>
            Obligatorio
          </th>

          <th>
            Estado
          </th>

          <th>
            Archivo digital
          </th>
        </tr>
      </thead>

      <tbody>
        ${documentos}
      </tbody>
    </table>
  </section>

  <section class="section">
    <h2 class="section-title">
      Observaciones
    </h2>

    <div class="observations">
      ${escapeHtml(
        valueOrDash(
          expediente.observaciones,
        ),
      )}
    </div>
  </section>

  <section class="section">
    <div class="grid">
      <div>
        <span class="label">
          Expediente creado
        </span>

        <span class="value">
          ${escapeHtml(
            formatDateTime(
              expediente.creado_en,
            ),
          )}
        </span>
      </div>

      <div>
        <span class="label">
          Última actualización
        </span>

        <span class="value">
          ${escapeHtml(
            formatDateTime(
              expediente
                .actualizado_en,
            ),
          )}
        </span>
      </div>
    </div>
  </section>

  <section class="signatures">
    <div class="signature">
      Responsable de expediente

      <small>
        Firma y sello
      </small>
    </div>

    <div class="signature">
      Encargado

      <small>
        Firma
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