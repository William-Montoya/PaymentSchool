import {
  AlertTriangle,
  BarChart3,
  Download,
  FileText,
  Printer,
  Search,
  Users,
  WalletCards,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react'

import {
  useQuery,
} from '@tanstack/react-query'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  getDashboardFinanciero,
  getDeudaPorEstudiante,
  getDeudaPorGrado,
  getEstadoCuenta,
  getEstudiantesInsolventes,
} from '../api/reportes'

import type {
  DeudaPorEstudiante,
  EstadoCuentaItem,
  EstudianteInsolvente,
} from '../types/reporte'

import '../styles/students.css'
import '../styles/reports.css'


type ReportTab =
  | 'RESUMEN'
  | 'DEUDA'
  | 'INSOLVENTES'
  | 'ESTADO_CUENTA'


const tabLabels: Record<
  ReportTab,
  string
> = {
  RESUMEN:
    'Resumen financiero',
  DEUDA:
    'Deuda por estudiante',
  INSOLVENTES:
    'Insolventes',
  ESTADO_CUENTA:
    'Estado de cuenta',
}


function formatMoney(
  value: string | number,
) {
  return new Intl.NumberFormat(
    'es-GT',
    {
      style: 'currency',
      currency: 'GTQ',
    },
  ).format(
    Number(value),
  )
}


function formatDate(
  value: string | null,
) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    },
  ).format(
    new Date(
      `${value}T00:00:00`,
    ),
  )
}


function csvCell(
  value:
    string |
    number |
    null |
    undefined,
) {
  const text =
    value === null ||
    value === undefined
      ? ''
      : String(value)

  return `"${text.replace(
    /"/g,
    '""',
  )}"`
}


function downloadCsv(
  filename: string,
  headers: string[],
  rows: (
    string |
    number |
    null |
    undefined
  )[][],
) {
  const content = [
    headers
      .map(csvCell)
      .join(','),
    ...rows.map(
      (row) =>
        row
          .map(csvCell)
          .join(','),
    ),
  ].join('\n')

  const blob = new Blob(
    ['\ufeff', content],
    {
      type:
        'text/csv;charset=utf-8;',
    },
  )

  const url =
    URL.createObjectURL(blob)

  const link =
    document.createElement('a')

  link.href = url
  link.download = filename

  document.body.appendChild(
    link,
  )

  link.click()
  link.remove()

  URL.revokeObjectURL(url)
}


function ReportsPage() {
  const [
    activeTab,
    setActiveTab,
  ] = useState<ReportTab>(
    'RESUMEN',
  )

  const [
    debtSearchDraft,
    setDebtSearchDraft,
  ] = useState('')

  const [
    debtSearch,
    setDebtSearch,
  ] = useState('')

  const [
    insolventSearchDraft,
    setInsolventSearchDraft,
  ] = useState('')

  const [
    insolventSearch,
    setInsolventSearch,
  ] = useState('')

  const [
    studentSearchDraft,
    setStudentSearchDraft,
  ] = useState('')

  const [
    studentSearch,
    setStudentSearch,
  ] = useState('')

  const [
    selectedStudent,
    setSelectedStudent,
  ] = useState<
    DeudaPorEstudiante |
    null
  >(null)

  const dashboardQuery =
    useQuery({
      queryKey: [
        'reportes-dashboard',
      ],
      queryFn:
        getDashboardFinanciero,
    })

  const debtByGradeQuery =
    useQuery({
      queryKey: [
        'reportes-deuda-grado',
      ],
      queryFn:
        getDeudaPorGrado,
    })

  const debtQuery =
    useQuery({
      queryKey: [
        'reportes-deuda-estudiante',
        debtSearch,
      ],
      queryFn: () =>
        getDeudaPorEstudiante({
          buscar:
            debtSearch ||
            undefined,
          offset: 0,
          limit: 200,
        }),
      enabled:
        activeTab === 'DEUDA',
    })

  const insolventQuery =
    useQuery({
      queryKey: [
        'reportes-insolventes',
        insolventSearch,
      ],
      queryFn: () =>
        getEstudiantesInsolventes({
          buscar:
            insolventSearch ||
            undefined,
          offset: 0,
          limit: 200,
        }),
      enabled:
        activeTab ===
        'INSOLVENTES',
    })

  const studentsQuery =
    useQuery({
      queryKey: [
        'reportes-estudiantes',
        studentSearch,
      ],
      queryFn: () =>
        getDeudaPorEstudiante({
          offset: 0,
          limit: 50,
          buscar:
            studentSearch ||
            undefined,
        }),
      enabled:
        activeTab ===
          'ESTADO_CUENTA' &&
        selectedStudent ===
          null,
    })

  const accountQuery =
    useQuery({
      queryKey: [
        'reportes-estado-cuenta',
        selectedStudent
          ?.id_estudiante,
      ],
      queryFn: () =>
        getEstadoCuenta(
          selectedStudent!
            .id_estudiante,
        ),
      enabled:
        activeTab ===
          'ESTADO_CUENTA' &&
        selectedStudent !==
          null,
    })

  const accountSummary =
    useMemo(
      () =>
        (
          accountQuery.data ??
          []
        ).reduce(
          (
            current,
            item,
          ) => ({
            pagado:
              current.pagado +
              Number(
                item.total_pagado,
              ),
            saldo:
              current.saldo +
              Number(
                item.saldo,
              ),
          }),
          {
            pagado: 0,
            saldo: 0,
          },
        ),
      [
        accountQuery.data,
      ],
    )

  function handleDebtSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setDebtSearch(
      debtSearchDraft.trim(),
    )
  }

  function handleInsolventSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setInsolventSearch(
      insolventSearchDraft
        .trim(),
    )
  }

  function handleStudentSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setStudentSearch(
      studentSearchDraft
        .trim(),
    )
  }

  function printReport() {
    window.print()
  }

  function exportDebt(
    rows:
      DeudaPorEstudiante[],
  ) {
    downloadCsv(
      'deuda-por-estudiante.csv',
      [
        'Carnet',
        'Estudiante',
        'Grado',
        'Deuda',
      ],
      rows.map(
        (item) => [
          item.codigo_estudiante,
          item.estudiante,
          item.grado,
          item.deuda_total,
        ],
      ),
    )
  }

  function exportInsolvent(
    rows:
      EstudianteInsolvente[],
  ) {
    downloadCsv(
      'estudiantes-insolventes.csv',
      [
        'Carnet',
        'Estudiante',
        'Grado',
        'Inscripción',
        'Deuda',
      ],
      rows.map(
        (item) => [
          item.codigo_estudiante,
          item.estudiante,
          item.grado,
          item.id_inscripcion,
          item.deuda_total,
        ],
      ),
    )
  }

  function exportAccount(
    rows:
      EstadoCuentaItem[],
  ) {
    const code =
      selectedStudent
        ?.codigo_estudiante ??
      'estudiante'

    downloadCsv(
      `estado-cuenta-${code}.csv`,
      [
        'Carnet',
        'Estudiante',
        'Carrera',
        'Grado',
        'Concepto',
        'Período',
        'Vencimiento',
        'Pagado',
        'Saldo',
      ],
      rows.map(
        (item) => [
          item.codigo_estudiante,
          item.estudiante,
          item.carrera,
          item.grado,
          item.concepto,
          item.periodo,
          item.fecha_vencimiento,
          item.total_pagado,
          item.saldo,
        ],
      ),
    )
  }

  const dashboard =
    dashboardQuery.data

  const debtByGrade =
    debtByGradeQuery.data ??
    []

  const debtRows =
    debtQuery.data ??
    []

  const insolventRows =
    insolventQuery.data ??
    []

  const studentRows =
    studentsQuery.data ??
    []

  const accountRows =
    accountQuery.data ??
    []

  return (
    <main className="reports-page">
      <header className="reports-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Reportes
          </span>

          <h1>
            Reportes y estados financieros
          </h1>

          <p>
            Deuda, morosidad y estados
            de cuenta con información
            actual del sistema.
          </p>
        </div>

        <button
          className="button button-secondary reports-print-button reports-no-print"
          type="button"
          onClick={printReport}
        >
          <Printer
            size={16}
            aria-hidden="true"
          />

          Imprimir
        </button>
      </header>

      <section className="reports-tabs reports-no-print">
        {(
          Object.entries(
            tabLabels,
          ) as [
            ReportTab,
            string,
          ][]
        ).map(
          ([
            value,
            label,
          ]) => (
            <button
              key={value}
              className={
                activeTab === value
                  ? 'reports-tab reports-tab-active'
                  : 'reports-tab'
              }
              type="button"
              onClick={() =>
                setActiveTab(
                  value,
                )
              }
            >
              {label}
            </button>
          ),
        )}
      </section>

      {activeTab ===
        'RESUMEN' && (
        <div className="reports-content">
          {dashboardQuery
            .isError ? (
            <section className="reports-message reports-message-error">
              {getApiErrorMessage(
                dashboardQuery.error,
                'No fue posible cargar el resumen financiero.',
              )}
            </section>
          ) : dashboardQuery
              .isLoading ||
            !dashboard ? (
            <section className="reports-message">
              Cargando resumen...
            </section>
          ) : (
            <>
              <section className="reports-kpi-grid">
                <ReportKpi
                  icon={
                    <Users
                      size={20}
                    />
                  }
                  label="Estudiantes activos"
                  value={
                    dashboard
                      .estudiantes_activos
                  }
                />

                <ReportKpi
                  icon={
                    <FileText
                      size={20}
                    />
                  }
                  label="Inscripciones activas"
                  value={
                    dashboard
                      .inscripciones_activas
                  }
                />

                <ReportKpi
                  icon={
                    <WalletCards
                      size={20}
                    />
                  }
                  label="Total pagado"
                  value={
                    formatMoney(
                      dashboard
                        .total_pagado,
                    )
                  }
                />

                <ReportKpi
                  icon={
                    <AlertTriangle
                      size={20}
                    />
                  }
                  label="Deuda total"
                  value={
                    formatMoney(
                      dashboard
                        .deuda_total,
                    )
                  }
                />

                <ReportKpi
                  icon={
                    <BarChart3
                      size={20}
                    />
                  }
                  label="Insolventes"
                  value={
                    dashboard
                      .estudiantes_insolventes
                  }
                />
              </section>

              <section className="module-card">
                <header className="reports-section-header">
                  <div>
                    <h2>
                      Deuda por grado
                    </h2>

                    <p>
                      Saldos acumulados
                      por grado.
                    </p>
                  </div>

                  <button
                    className="button button-secondary reports-no-print"
                    type="button"
                    disabled={
                      debtByGrade
                        .length === 0
                    }
                    onClick={() =>
                      downloadCsv(
                        'deuda-por-grado.csv',
                        [
                          'Grado',
                          'Estudiantes',
                          'Deuda',
                        ],
                        debtByGrade.map(
                          (item) => [
                            item.grado,
                            item
                              .cantidad_estudiantes,
                            item
                              .deuda_total,
                          ],
                        ),
                      )
                    }
                  >
                    <Download
                      size={16}
                      aria-hidden="true"
                    />

                    Exportar CSV
                  </button>
                </header>

                {debtByGradeQuery
                  .isLoading ? (
                  <div className="reports-message">
                    Cargando deuda por grado...
                  </div>
                ) : debtByGradeQuery
                    .isError ? (
                  <div className="reports-message reports-message-error">
                    {getApiErrorMessage(
                      debtByGradeQuery
                        .error,
                      'No fue posible cargar la deuda por grado.',
                    )}
                  </div>
                ) : (
                  <ReportTable>
                    <thead>
                      <tr>
                        <th>
                          Grado
                        </th>

                        <th>
                          Estudiantes
                        </th>

                        <th className="text-right">
                          Deuda
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {debtByGrade.map(
                        (item) => (
                          <tr
                            key={
                              item
                                .id_grado
                            }
                          >
                            <td>
                              <strong>
                                {
                                  item.grado
                                }
                              </strong>
                            </td>

                            <td>
                              {
                                item
                                  .cantidad_estudiantes
                              }
                            </td>

                            <td className="text-right reports-money">
                              {formatMoney(
                                item
                                  .deuda_total,
                              )}
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>
                  </ReportTable>
                )}
              </section>
            </>
          )}
        </div>
      )}

      {activeTab ===
        'DEUDA' && (
        <ReportListSection
          title="Deuda por estudiante"
          description="Consulta estudiantes con saldo pendiente."
          searchDraft={
            debtSearchDraft
          }
          onSearchDraft={
            setDebtSearchDraft
          }
          onSearch={
            handleDebtSearch
          }
          loading={
            debtQuery.isLoading
          }
          error={
            debtQuery.isError
              ? getApiErrorMessage(
                  debtQuery.error,
                  'No fue posible cargar la deuda por estudiante.',
                )
              : null
          }
          exportDisabled={
            debtRows.length === 0
          }
          onExport={() =>
            exportDebt(
              debtRows,
            )
          }
        >
          {debtRows.length === 0 ? (
            <div className="reports-empty">
              No hay resultados.
            </div>
          ) : (
            <ReportTable>
              <thead>
                <tr>
                  <th>Carnet</th>
                  <th>Estudiante</th>
                  <th>Grado</th>
                  <th className="text-right">
                    Deuda
                  </th>
                </tr>
              </thead>

              <tbody>
                {debtRows.map(
                  (item) => (
                    <tr
                      key={
                        item
                          .id_estudiante
                      }
                    >
                      <td>
                        <strong>
                          {
                            item
                              .codigo_estudiante
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          item
                            .estudiante
                        }
                      </td>

                      <td>
                        {item.grado}
                      </td>

                      <td className="text-right reports-money">
                        {formatMoney(
                          item
                            .deuda_total,
                        )}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </ReportTable>
          )}
        </ReportListSection>
      )}

      {activeTab ===
        'INSOLVENTES' && (
        <ReportListSection
          title="Estudiantes insolventes"
          description="Estudiantes con obligaciones pendientes."
          searchDraft={
            insolventSearchDraft
          }
          onSearchDraft={
            setInsolventSearchDraft
          }
          onSearch={
            handleInsolventSearch
          }
          loading={
            insolventQuery
              .isLoading
          }
          error={
            insolventQuery.isError
              ? getApiErrorMessage(
                  insolventQuery.error,
                  'No fue posible cargar los estudiantes insolventes.',
                )
              : null
          }
          exportDisabled={
            insolventRows.length ===
            0
          }
          onExport={() =>
            exportInsolvent(
              insolventRows,
            )
          }
        >
          {insolventRows.length === 0 ? (
            <div className="reports-empty">
              No hay resultados.
            </div>
          ) : (
            <ReportTable>
              <thead>
                <tr>
                  <th>Carnet</th>
                  <th>Estudiante</th>
                  <th>Grado</th>
                  <th>Inscripción</th>
                  <th className="text-right">
                    Deuda
                  </th>
                </tr>
              </thead>

              <tbody>
                {insolventRows.map(
                  (item) => (
                    <tr
                      key={
                        item
                          .id_inscripcion
                      }
                    >
                      <td>
                        <strong>
                          {
                            item
                              .codigo_estudiante
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          item
                            .estudiante
                        }
                      </td>

                      <td>
                        {item.grado}
                      </td>

                      <td>
                        #
                        {
                          item
                            .id_inscripcion
                        }
                      </td>

                      <td className="text-right reports-money">
                        {formatMoney(
                          item
                            .deuda_total,
                        )}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </ReportTable>
          )}
        </ReportListSection>
      )}

      {activeTab ===
        'ESTADO_CUENTA' && (
        <section className="reports-content">
          {!selectedStudent ? (
            <section className="module-card">
              <header className="reports-section-header">
                <div>
                  <h2>
                    Estado de cuenta
                  </h2>

                  <p>
                    Busca y selecciona
                    un estudiante.
                  </p>
                </div>
              </header>

              <form
                className="reports-search reports-no-print"
                onSubmit={
                  handleStudentSearch
                }
              >
                <Search
                  size={18}
                  aria-hidden="true"
                />

                <input
                  type="search"
                  value={
                    studentSearchDraft
                  }
                  placeholder="Carnet, nombre, apellido o CUI..."
                  onChange={(event) =>
                    setStudentSearchDraft(
                      event.target.value,
                    )
                  }
                />

                <button type="submit">
                  Buscar
                </button>
              </form>

              {studentsQuery
                .isLoading ? (
                <div className="reports-message">
                  Cargando estudiantes...
                </div>
              ) : studentsQuery
                  .isError ? (
                <div className="reports-message reports-message-error">
                  {getApiErrorMessage(
                    studentsQuery.error,
                    'No fue posible cargar los estudiantes.',
                  )}
                </div>
              ) : studentRows
                  .length === 0 ? (
                <div className="reports-empty">
                  No hay estudiantes.
                </div>
              ) : (
                <ReportTable>
                  <thead>
                    <tr>
                      <th>Carnet</th>
                      <th>Estudiante</th>
                      <th>Grado</th>
                      <th className="text-right">
                        Deuda
                      </th>
                      <th>Acción</th>
                    </tr>
                  </thead>

                  <tbody>
                    {studentRows.map(
                      (student) => (
                        <tr
                          key={
                            student
                              .id_estudiante
                          }
                        >
                          <td>
                            <strong>
                              {
                                student
                                  .codigo_estudiante
                              }
                            </strong>
                          </td>

                          <td>
                            {student.estudiante}
                          </td>

                          <td>
                            {student.grado}
                          </td>

                          <td className="text-right reports-money">
                            {formatMoney(
                              student.deuda_total,
                            )}
                          </td>

                          <td>
                            <button
                              className="button button-secondary reports-no-print"
                              type="button"
                              onClick={() =>
                                setSelectedStudent(
                                  student,
                                )
                              }
                            >
                              Ver estado
                            </button>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </ReportTable>
              )}
            </section>
          ) : (
            <>
              <section className="module-card reports-account-header">
                <div>
                  <span className="dashboard-card-eyebrow">
                    {
                      selectedStudent
                        .codigo_estudiante
                    }
                  </span>

                  <h2>
                    {selectedStudent.estudiante}
                  </h2>
                </div>

                <div className="reports-account-actions reports-no-print">
                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={() =>
                      setSelectedStudent(
                        null,
                      )
                    }
                  >
                    Cambiar estudiante
                  </button>

                  <button
                    className="button button-secondary"
                    type="button"
                    disabled={
                      accountRows
                        .length === 0
                    }
                    onClick={() =>
                      exportAccount(
                        accountRows,
                      )
                    }
                  >
                    <Download
                      size={16}
                      aria-hidden="true"
                    />

                    Exportar CSV
                  </button>
                </div>
              </section>

              <section className="reports-account-summary">
                <article className="module-card">
                  <span>
                    Total pagado
                  </span>

                  <strong>
                    {formatMoney(
                      accountSummary
                        .pagado,
                    )}
                  </strong>
                </article>

                <article className="module-card">
                  <span>
                    Saldo pendiente
                  </span>

                  <strong>
                    {formatMoney(
                      accountSummary
                        .saldo,
                    )}
                  </strong>
                </article>

                <article className="module-card">
                  <span>
                    Obligaciones
                  </span>

                  <strong>
                    {
                      accountRows
                        .length
                    }
                  </strong>
                </article>
              </section>

              <section className="module-card">
                {accountQuery
                  .isLoading ? (
                  <div className="reports-message">
                    Cargando estado de cuenta...
                  </div>
                ) : accountQuery
                    .isError ? (
                  <div className="reports-message reports-message-error">
                    {getApiErrorMessage(
                      accountQuery.error,
                      'No fue posible cargar el estado de cuenta.',
                    )}
                  </div>
                ) : accountRows
                    .length === 0 ? (
                  <div className="reports-empty">
                    El estudiante no tiene
                    movimientos en el estado
                    de cuenta.
                  </div>
                ) : (
                  <ReportTable>
                    <thead>
                      <tr>
                        <th>
                          Carrera / Grado
                        </th>
                        <th>
                          Concepto
                        </th>
                        <th>
                          Período
                        </th>
                        <th>
                          Vencimiento
                        </th>
                        <th className="text-right">
                          Pagado
                        </th>
                        <th className="text-right">
                          Saldo
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {accountRows.map(
                        (item) => (
                          <tr
                            key={
                              item
                                .id_obligacion
                            }
                          >
                            <td>
                              <strong>
                                {
                                  item
                                    .carrera
                                }
                              </strong>

                              <div className="reports-secondary">
                                {
                                  item
                                    .grado
                                }
                              </div>
                            </td>

                            <td>
                              {
                                item
                                  .concepto
                              }
                            </td>

                            <td>
                              {item.periodo ||
                                '—'}
                            </td>

                            <td>
                              {formatDate(
                                item
                                  .fecha_vencimiento,
                              )}
                            </td>

                            <td className="text-right">
                              {formatMoney(
                                item
                                  .total_pagado,
                              )}
                            </td>

                            <td className="text-right reports-money">
                              {formatMoney(
                                item.saldo,
                              )}
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>
                  </ReportTable>
                )}
              </section>
            </>
          )}
        </section>
      )}
    </main>
  )
}


interface ReportKpiProps {
  icon: ReactNode
  label: string
  value: string | number
}


function ReportKpi({
  icon,
  label,
  value,
}: ReportKpiProps) {
  return (
    <article className="reports-kpi">
      {icon}

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </article>
  )
}


interface ReportListSectionProps {
  title: string
  description: string
  searchDraft: string
  onSearchDraft:
    (value: string) => void
  onSearch:
    (
      event:
        FormEvent<HTMLFormElement>,
    ) => void
  loading: boolean
  error: string | null
  exportDisabled: boolean
  onExport: () => void
  children: ReactNode
}


function ReportListSection({
  title,
  description,
  searchDraft,
  onSearchDraft,
  onSearch,
  loading,
  error,
  exportDisabled,
  onExport,
  children,
}: ReportListSectionProps) {
  return (
    <section className="reports-content">
      <section className="module-card">
        <header className="reports-section-header">
          <div>
            <h2>
              {title}
            </h2>

            <p>
              {description}
            </p>
          </div>

          <button
            className="button button-secondary reports-no-print"
            type="button"
            disabled={
              exportDisabled
            }
            onClick={onExport}
          >
            <Download
              size={16}
              aria-hidden="true"
            />

            Exportar CSV
          </button>
        </header>

        <form
          className="reports-search reports-no-print"
          onSubmit={onSearch}
        >
          <Search
            size={18}
            aria-hidden="true"
          />

          <input
            type="search"
            value={searchDraft}
            placeholder="Carnet, estudiante o grado..."
            onChange={(event) =>
              onSearchDraft(
                event.target.value,
              )
            }
          />

          <button type="submit">
            Buscar
          </button>
        </form>

        {loading ? (
          <div className="reports-message">
            Cargando reporte...
          </div>
        ) : error ? (
          <div className="reports-message reports-message-error">
            {error}
          </div>
        ) : (
          children
        )}
      </section>
    </section>
  )
}


interface ReportTableProps {
  children: ReactNode
}


function ReportTable({
  children,
}: ReportTableProps) {
  return (
    <div className="reports-table-wrapper">
      <table className="reports-table">
        {children}
      </table>
    </div>
  )
}


export default ReportsPage
