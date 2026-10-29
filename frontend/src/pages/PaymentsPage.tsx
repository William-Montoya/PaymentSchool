import {
  ArrowLeft,
  Eye,
  Search,
  WalletCards,
} from 'lucide-react'

import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getContactos,
} from '../api/contactos'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  getEstudiante,
} from '../api/estudiantes'

import {
  getInscripcionesFinanzas,
  getObligacion,
  getObligaciones,
} from '../api/obligaciones'

import {
  generarReciboPago,
  getComprobantePago,
  getPagos,
  registrarCobro,
} from '../api/pagos'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import ReceiptModal from
  '../components/pagos/ReceiptModal'

import StudentSearchModal, {
  type PagoStudentSelection,
} from '../components/pagos/StudentSearchModal'

import type {
  InscripcionFinanzas,
  ObligacionSaldo,
} from '../types/obligacion'

import type {
  ComprobantePagoResponse,
  MetodoPago,
} from '../types/pago'

import '../styles/students.css'
import '../styles/finances.css'
import '../styles/payments.css'

interface PaymentObligationItem {
  obligacion: ObligacionSaldo
  inscripcion: InscripcionFinanzas
}

interface ReceiptState {
  comprobante: ComprobantePagoResponse
  obligaciones: Record<number, ObligacionSaldo>
}

const methodLabels: Record<MetodoPago, string> = {
  EFECTIVO: 'Efectivo',
  TRANSFERENCIA: 'Transferencia',
  DEPOSITO: 'Depósito',
  TARJETA: 'Tarjeta',
  OTRO: 'Otro',
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

function compareObligations(
  left: PaymentObligationItem,
  right: PaymentObligationItem,
): number {
  const leftDate = left.obligacion.fecha_vencimiento ?? '9999-12-31'
  const rightDate = right.obligacion.fecha_vencimiento ?? '9999-12-31'

  if (leftDate !== rightDate) {
    return leftDate.localeCompare(rightDate)
  }

  const leftPeriod = left.obligacion.periodo ?? '9999-99'
  const rightPeriod = right.obligacion.periodo ?? '9999-99'

  if (leftPeriod !== rightPeriod) {
    return leftPeriod.localeCompare(rightPeriod)
  }

  return left.obligacion.id_obligacion - right.obligacion.id_obligacion
}

function PaymentsPage() {
  const queryClient = useQueryClient()
  const codeInputRef = useRef<HTMLInputElement>(null)

  const { hasAnyPermission } = useAuth()

  const canRegister = hasAnyPermission([
    PERMISSIONS.PAGOS_REGISTRAR,
  ])

  const canViewContacts = hasAnyPermission([
    PERMISSIONS.EXPEDIENTES_VER,
  ])

  const [codeSearch, setCodeSearch] = useState('')
  const [codeLoading, setCodeLoading] = useState(false)
  const [codeError, setCodeError] = useState<string | null>(null)
  const [showStudentSearch, setShowStudentSearch] = useState(false)

  const [selectedStudent, setSelectedStudent] =
    useState<PagoStudentSelection | null>(null)

  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState<MetodoPago>('EFECTIVO')
  const [reference, setReference] = useState('')
  const [observations, setObservations] = useState('')

  const [receiptState, setReceiptState] =
    useState<ReceiptState | null>(null)
  const [receiptLoading, setReceiptLoading] = useState(false)
  const [receiptError, setReceiptError] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedStudent) {
      codeInputRef.current?.focus()
    }
  }, [selectedStudent])

  const inscripcionesQuery = useQuery({
    queryKey: [
      'pagos-inscripciones-estudiante',
      selectedStudent?.id_estudiante,
    ],
    queryFn: async () => {
      const data = await getInscripcionesFinanzas({
        buscar: selectedStudent!.codigo_estudiante,
        limit: 100,
      })

      return data.filter(
        (inscripcion) =>
          inscripcion.id_estudiante === selectedStudent!.id_estudiante,
      )
    },
    enabled: selectedStudent !== null,
  })

  const inscripciones = inscripcionesQuery.data ?? []

  const obligacionesQuery = useQuery({
    queryKey: [
      'pagos-obligaciones-estudiante',
      selectedStudent?.id_estudiante,
      inscripciones.map((item) => item.id_inscripcion),
    ],
    queryFn: async (): Promise<PaymentObligationItem[]> => {
      const groups = await Promise.all(
        inscripciones.map(async (inscripcion) => {
          const obligaciones = await getObligaciones({
            id_inscripcion: inscripcion.id_inscripcion,
          })

          return obligaciones.map((obligacion) => ({
            obligacion,
            inscripcion,
          }))
        }),
      )

      return groups.flat()
    },
    enabled:
      selectedStudent !== null &&
      inscripciones.length > 0,
  })

  const estudianteQuery = useQuery({
    queryKey: [
      'pagos-estudiante-detalle',
      selectedStudent?.id_estudiante,
    ],
    queryFn: () => getEstudiante(selectedStudent!.id_estudiante),
    enabled: selectedStudent !== null,
  })

  const contactosQuery = useQuery({
    queryKey: [
      'pagos-contactos-estudiante',
      selectedStudent?.id_estudiante,
    ],
    queryFn: () => getContactos(selectedStudent!.id_estudiante, true),
    enabled:
      selectedStudent !== null &&
      canViewContacts,
  })

  const pagosQuery = useQuery({
    queryKey: [
      'pagos-historial-estudiante',
      selectedStudent?.id_estudiante,
    ],
    queryFn: () => getPagos({
      id_estudiante: selectedStudent!.id_estudiante,
    }),
    enabled: selectedStudent !== null,
  })

  const openObligations = useMemo(() => {
    return (obligacionesQuery.data ?? [])
      .filter(({ obligacion }) =>
        (obligacion.estado === 'PENDIENTE' ||
          obligacion.estado === 'PARCIAL') &&
        Number(obligacion.saldo) > 0,
      )
      .sort(compareObligations)
  }, [obligacionesQuery.data])

  const selectedItems = useMemo(() => {
    const selectedSet = new Set(selectedIds)

    return openObligations.filter(({ obligacion }) =>
      selectedSet.has(obligacion.id_obligacion),
    )
  }, [openObligations, selectedIds])

  const totalPending = useMemo(
    () => openObligations.reduce(
      (total, item) => total + Number(item.obligacion.saldo),
      0,
    ),
    [openObligations],
  )

  const pendingMonths = useMemo(
    () => openObligations.filter(
      (item) => item.obligacion.tipo_obligacion === 'MENSUALIDAD',
    ).length,
    [openObligations],
  )

  const otherPending = openObligations.length - pendingMonths

  const selectedTotal = useMemo(
    () => selectedItems.reduce(
      (total, item) => total + Number(item.obligacion.saldo),
      0,
    ),
    [selectedItems],
  )

  const amountNumber = Number(amount || 0)

  const applicationPreview = useMemo(() => {
    let remaining = Number.isFinite(amountNumber)
      ? Math.max(amountNumber, 0)
      : 0

    const map = new Map<number, number>()

    for (const item of selectedItems) {
      const balance = Number(item.obligacion.saldo)
      const applied = Math.min(remaining, balance)

      map.set(item.obligacion.id_obligacion, applied)
      remaining -= applied
    }

    return map
  }, [amountNumber, selectedItems])

  const currentInscription = useMemo(() => {
    return (
      inscripciones.find((item) => item.estado === 'ACTIVA') ??
      inscripciones[0] ??
      null
    )
  }, [inscripciones])

  const preferredContact = useMemo(() => {
    const contacts = contactosQuery.data ?? []

    return (
      contacts.find((contact) => contact.es_principal) ??
      contacts.find((contact) => Boolean(contact.whatsapp)) ??
      contacts.find((contact) => Boolean(contact.telefono)) ??
      null
    )
  }, [contactosQuery.data])

  useEffect(() => {
    if (selectedTotal > 0) {
      setAmount(selectedTotal.toFixed(2))
    } else {
      setAmount('')
    }
  }, [selectedTotal])

  const cobroMutation = useMutation({
    mutationFn: registrarCobro,
    onSuccess: async (result) => {
      setSelectedIds([])
      setAmount('')
      setReference('')
      setObservations('')

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [
            'pagos-obligaciones-estudiante',
            selectedStudent?.id_estudiante,
          ],
        }),
        queryClient.invalidateQueries({
          queryKey: [
            'pagos-historial-estudiante',
            selectedStudent?.id_estudiante,
          ],
        }),
      ])

      await openReceipt(result.pago.id_pago)
    },
  })

  function applyStudentSelection(
    selection: PagoStudentSelection,
  ) {
    setSelectedStudent(selection)
    setCodeSearch(selection.codigo_estudiante)
    setCodeError(null)
    setSelectedIds([])
    setReceiptError(null)
    setShowStudentSearch(false)
    cobroMutation.reset()
  }

  async function handleCodeSearch(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const code = codeSearch.trim().toUpperCase()

    if (!code) {
      setCodeError('Ingresa el código o carnet del estudiante.')
      return
    }

    setCodeLoading(true)
    setCodeError(null)

    try {
      const data = await getInscripcionesFinanzas({
        buscar: code,
        limit: 100,
      })

      const exact = data.filter(
        (item) => item.codigo_estudiante.toUpperCase() === code,
      )

      if (exact.length === 0) {
        setCodeError(
          'No se encontró una inscripción con ese carnet. Usa Buscar estudiante si no conoces el código exacto.',
        )
        return
      }

      const first = exact[0]

      applyStudentSelection({
        id_estudiante: first.id_estudiante,
        codigo_estudiante: first.codigo_estudiante,
        estudiante: first.estudiante,
        inscripciones: exact,
      })
    } catch (searchError) {
      setCodeError(
        getApiErrorMessage(
          searchError,
          'No fue posible buscar el estudiante.',
        ),
      )
    } finally {
      setCodeLoading(false)
    }
  }

  function clearStudent() {
    setSelectedStudent(null)
    setCodeSearch('')
    setCodeError(null)
    setSelectedIds([])
    setAmount('')
    setMethod('EFECTIVO')
    setReference('')
    setObservations('')
    setReceiptState(null)
    setReceiptError(null)
    cobroMutation.reset()
  }

  function toggleObligation(item: PaymentObligationItem) {
    const id = item.obligacion.id_obligacion
    const currentlySelected = selectedIds.includes(id)

    if (item.obligacion.tipo_obligacion !== 'MENSUALIDAD') {
      setSelectedIds((current) =>
        currentlySelected
          ? current.filter((currentId) => currentId !== id)
          : [...current, id],
      )
      return
    }

    const monthly = openObligations.filter(
      (candidate) =>
        candidate.inscripcion.id_inscripcion ===
          item.inscripcion.id_inscripcion &&
        candidate.obligacion.tipo_obligacion === 'MENSUALIDAD',
    )

    const index = monthly.findIndex(
      (candidate) => candidate.obligacion.id_obligacion === id,
    )

    if (index < 0) {
      return
    }

    if (!currentlySelected) {
      const requiredIds = monthly
        .slice(0, index + 1)
        .map((candidate) => candidate.obligacion.id_obligacion)

      setSelectedIds((current) =>
        Array.from(new Set([...current, ...requiredIds])),
      )
      return
    }

    const idsToRemove = new Set(
      monthly
        .slice(index)
        .map((candidate) => candidate.obligacion.id_obligacion),
    )

    setSelectedIds((current) =>
      current.filter((currentId) => !idsToRemove.has(currentId)),
    )
  }

  async function openReceipt(idPago: number) {
    setReceiptLoading(true)
    setReceiptError(null)

    try {
      let comprobante = await getComprobantePago(idPago)

      if (!comprobante.recibo && canRegister) {
        await generarReciboPago(idPago)
        comprobante = await getComprobantePago(idPago)
      }

      const details = await Promise.all(
        comprobante.aplicaciones.map((application) =>
          getObligacion(application.id_obligacion),
        ),
      )

      const detailMap: Record<number, ObligacionSaldo> = {}

      for (const detail of details) {
        detailMap[detail.id_obligacion] = detail
      }

      setReceiptState({
        comprobante,
        obligaciones: detailMap,
      })
    } catch (error) {
      setReceiptError(
        getApiErrorMessage(
          error,
          'No fue posible cargar el comprobante.',
        ),
      )
    } finally {
      setReceiptLoading(false)
    }
  }

  function handlePay(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedStudent) {
      return
    }

    if (selectedIds.length === 0) {
      return
    }

    if (!Number.isFinite(amountNumber) || amountNumber <= 0) {
      return
    }

    if (amountNumber > selectedTotal) {
      return
    }

    cobroMutation.mutate({
      id_estudiante: selectedStudent.id_estudiante,
      id_obligaciones: selectedIds,
      monto: amountNumber.toFixed(2),
      metodo: method,
      referencia: reference.trim() || null,
      observaciones: observations.trim() || null,
    })
  }

  const paymentError = cobroMutation.isError
    ? getApiErrorMessage(
        cobroMutation.error,
        'No fue posible registrar el pago.',
      )
    : null

  const studentReceiptInfo = {
    codigo: selectedStudent?.codigo_estudiante ?? '',
    nombre: estudianteQuery.data
      ? `${estudianteQuery.data.nombres} ${estudianteQuery.data.apellidos}`
      : selectedStudent?.estudiante ?? '',
    cui: estudianteQuery.data?.cui ?? null,
  }

  return (
    <>
      <main className="module-page">
        <header className="module-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Finanzas
            </span>

            <h1>Pagos</h1>

            <p>
              Caja, aplicación de obligaciones y emisión de recibos.
            </p>
          </div>

          {selectedStudent && (
            <button
              className="button button-secondary"
              type="button"
              onClick={clearStudent}
            >
              <ArrowLeft size={16} aria-hidden="true" />
              Otro estudiante
            </button>
          )}
        </header>

        {!selectedStudent ? (
          <section className="module-card payment-entry-card">
            <div className="payment-entry-heading">
              <WalletCards size={34} aria-hidden="true" />

              <div>
                <h2>Registrar pago</h2>
                <p>
                  Ingresa el carnet. El cursor queda preparado para
                  captura rápida en caja.
                </p>
              </div>
            </div>

            <form
              className="payment-code-search"
              onSubmit={handleCodeSearch}
            >
              <label htmlFor="payment-student-code">
                Código / Carnet
              </label>

              <div className="payment-code-row">
                <Search size={19} aria-hidden="true" />

                <input
                  ref={codeInputRef}
                  id="payment-student-code"
                  autoFocus
                  autoComplete="off"
                  value={codeSearch}
                  placeholder="EST-000013"
                  onChange={(event) =>
                    setCodeSearch(event.target.value.toUpperCase())
                  }
                />

                <button
                  className="button button-primary"
                  type="submit"
                  disabled={codeLoading}
                >
                  {codeLoading ? 'Buscando...' : 'Cargar'}
                </button>
              </div>
            </form>

            {codeError && (
              <div className="form-error" role="alert">
                {codeError}
              </div>
            )}

            <div className="payment-alternative-search">
              <span>¿No conoces el carnet?</span>

              <button
                className="button button-secondary"
                type="button"
                onClick={() => setShowStudentSearch(true)}
              >
                Buscar estudiante
              </button>
            </div>
          </section>
        ) : (
          <div className="payment-content">
            <section className="module-card finance-student-card">
              <div className="finance-student-main">
                <div className="finance-avatar">
                  {selectedStudent.estudiante.charAt(0).toUpperCase()}
                </div>

                <div>
                  <span className="dashboard-card-eyebrow">
                    {selectedStudent.codigo_estudiante}
                  </span>

                  <h2>{selectedStudent.estudiante}</h2>

                  <p>
                    {currentInscription
                      ? `${currentInscription.ciclo} · ${currentInscription.carrera} · ${currentInscription.grado}`
                      : 'Cargando información académica...'}
                  </p>
                </div>
              </div>

              <span className="finance-inscription-status finance-inscription-active">
                Caja
              </span>
            </section>

            <section className="payment-summary-grid">
              <article className="module-card">
                <span>Total pendiente</span>
                <strong>{formatMoney(totalPending)}</strong>
              </article>

              <article className="module-card">
                <span>Meses pendientes</span>
                <strong>{pendingMonths}</strong>
              </article>

              <article className="module-card">
                <span>Otros cargos</span>
                <strong>{otherPending}</strong>
              </article>

              <article className="module-card payment-selected-summary">
                <span>Seleccionado</span>
                <strong>{formatMoney(selectedTotal)}</strong>
              </article>
            </section>

            {receiptError && (
              <div className="module-message module-message-error">
                {receiptError}
              </div>
            )}

            <div className="payment-workspace">
              <section className="module-card payment-obligations-card">
                <header className="finance-section-header">
                  <div>
                    <h2>Obligaciones pendientes</h2>
                    <p>
                      Al seleccionar un mes se incluyen automáticamente
                      los meses anteriores que todavía tengan saldo.
                    </p>
                  </div>
                </header>

                {inscripcionesQuery.isLoading || obligacionesQuery.isLoading ? (
                  <div className="module-message">
                    Cargando obligaciones pendientes...
                  </div>
                ) : inscripcionesQuery.isError || obligacionesQuery.isError ? (
                  <div className="module-message module-message-error">
                    {getApiErrorMessage(
                      inscripcionesQuery.error ?? obligacionesQuery.error,
                      'No fue posible cargar las obligaciones del estudiante.',
                    )}
                  </div>
                ) : openObligations.length === 0 ? (
                  <div className="finance-empty payment-solvent-state">
                    <WalletCards size={38} aria-hidden="true" />
                    <strong>Sin obligaciones pendientes</strong>
                    <p>
                      El estudiante no tiene cargos con saldo pendiente.
                    </p>
                  </div>
                ) : (
                  <div className="module-table-wrapper payment-obligation-table">
                    <table className="module-table">
                      <thead>
                        <tr>
                          <th className="payment-checkbox-column">Pagar</th>
                          <th>Concepto</th>
                          <th>Período</th>
                          <th>Ciclo</th>
                          <th>Saldo</th>
                          <th>Se aplicará</th>
                        </tr>
                      </thead>

                      <tbody>
                        {openObligations.map((item) => {
                          const obligation = item.obligacion
                          const checked = selectedIds.includes(
                            obligation.id_obligacion,
                          )
                          const preview = applicationPreview.get(
                            obligation.id_obligacion,
                          ) ?? 0

                          return (
                            <tr
                              key={obligation.id_obligacion}
                              className={
                                checked ? 'payment-obligation-selected' : undefined
                              }
                            >
                              <td className="payment-checkbox-column">
                                <input
                                  type="checkbox"
                                  checked={checked}
                                  disabled={!canRegister}
                                  aria-label={`Seleccionar ${obligation.concepto}`}
                                  onChange={() => toggleObligation(item)}
                                />
                              </td>

                              <td>
                                <strong>{obligation.concepto}</strong>
                                <div className="finance-table-secondary">
                                  {obligation.tipo_obligacion}
                                  {obligation.estado === 'PARCIAL'
                                    ? ' · Abono previo'
                                    : ''}
                                </div>
                              </td>

                              <td>{formatPeriod(obligation.periodo)}</td>

                              <td>
                                <strong>{item.inscripcion.ciclo}</strong>
                                <div className="finance-table-secondary">
                                  {item.inscripcion.grado}
                                </div>
                              </td>

                              <td>
                                <strong>{formatMoney(obligation.saldo)}</strong>
                              </td>

                              <td>
                                {checked
                                  ? formatMoney(preview)
                                  : '—'}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>

              <aside className="module-card payment-cash-card">
                <header>
                  <span className="dashboard-card-eyebrow">
                    Recibo
                  </span>
                  <h2>Detalle del cobro</h2>
                  <p>
                    Selecciona obligaciones y registra el monto recibido.
                  </p>
                </header>

                <form className="payment-form" onSubmit={handlePay}>
                  <div className="payment-total-box">
                    <span>Total seleccionado</span>
                    <strong>{formatMoney(selectedTotal)}</strong>
                    <small>
                      {selectedIds.length} obligación
                      {selectedIds.length === 1 ? '' : 'es'} seleccionada
                      {selectedIds.length === 1 ? '' : 's'}
                    </small>
                  </div>

                  <label className="payment-field">
                    <span>Monto recibido *</span>
                    <input
                      type="number"
                      min="0.01"
                      step="0.01"
                      value={amount}
                      disabled={!canRegister || selectedIds.length === 0}
                      required
                      onChange={(event) => setAmount(event.target.value)}
                    />
                  </label>

                  {amountNumber > selectedTotal && selectedTotal > 0 && (
                    <div className="finance-warning-box">
                      El monto recibido no puede superar el saldo de las
                      obligaciones seleccionadas.
                    </div>
                  )}

                  <label className="payment-field">
                    <span>Método de pago *</span>
                    <select
                      value={method}
                      disabled={!canRegister}
                      onChange={(event) =>
                        setMethod(event.target.value as MetodoPago)
                      }
                    >
                      {Object.entries(methodLabels).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="payment-field">
                    <span>Referencia / No. boleta</span>
                    <input
                      value={reference}
                      maxLength={150}
                      disabled={!canRegister}
                      placeholder="Opcional"
                      onChange={(event) => setReference(event.target.value)}
                    />
                  </label>

                  <label className="payment-field">
                    <span>Observaciones</span>
                    <textarea
                      rows={3}
                      value={observations}
                      disabled={!canRegister}
                      placeholder="Opcional"
                      onChange={(event) => setObservations(event.target.value)}
                    />
                  </label>

                  {paymentError && (
                    <div className="form-error" role="alert">
                      {paymentError}
                    </div>
                  )}

                  {!canRegister && (
                    <div className="finance-info-box">
                      Tu usuario puede consultar saldos, pero no tiene el
                      permiso PAGOS_REGISTRAR.
                    </div>
                  )}

                  <button
                    className="button button-primary payment-submit-button"
                    type="submit"
                    disabled={
                      !canRegister ||
                      selectedIds.length === 0 ||
                      amountNumber <= 0 ||
                      amountNumber > selectedTotal ||
                      cobroMutation.isPending
                    }
                  >
                    {cobroMutation.isPending
                      ? 'Registrando pago...'
                      : 'Aplicar pago y generar recibo'}
                  </button>
                </form>
              </aside>
            </div>

            <section className="module-card payment-history-card">
              <header className="finance-section-header">
                <div>
                  <h2>Historial de pagos</h2>
                  <p>
                    Consulta y reimprime comprobantes del estudiante.
                  </p>
                </div>
              </header>

              {pagosQuery.isLoading ? (
                <div className="module-message">
                  Cargando historial...
                </div>
              ) : pagosQuery.isError ? (
                <div className="module-message module-message-error">
                  {getApiErrorMessage(
                    pagosQuery.error,
                    'No fue posible cargar el historial de pagos.',
                  )}
                </div>
              ) : (pagosQuery.data ?? []).length === 0 ? (
                <div className="finance-empty payment-history-empty">
                  <strong>Sin pagos registrados</strong>
                  <p>Este estudiante todavía no tiene pagos.</p>
                </div>
              ) : (
                <div className="module-table-wrapper">
                  <table className="module-table">
                    <thead>
                      <tr>
                        <th>Pago</th>
                        <th>Fecha</th>
                        <th>Método</th>
                        <th>Monto</th>
                        <th>Estado</th>
                        <th>Recibo</th>
                      </tr>
                    </thead>

                    <tbody>
                      {(pagosQuery.data ?? []).map((payment) => (
                        <tr key={payment.id_pago}>
                          <td>
                            <strong>#{payment.id_pago}</strong>
                          </td>

                          <td>{formatDateTime(payment.fecha_pago)}</td>
                          <td>{methodLabels[payment.metodo]}</td>
                          <td>{formatMoney(payment.monto_total)}</td>

                          <td>
                            <span className="finance-obligation-status">
                              {payment.estado}
                            </span>
                          </td>

                          <td className="table-action-column">
                            <button
                              className="table-icon-button"
                              type="button"
                              title="Ver / reimprimir recibo"
                              aria-label="Ver / reimprimir recibo"
                              disabled={receiptLoading}
                              onClick={() => void openReceipt(payment.id_pago)}
                            >
                              <Eye size={17} aria-hidden="true" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}
      </main>

      {showStudentSearch && (
        <StudentSearchModal
          onClose={() => setShowStudentSearch(false)}
          onSelect={applyStudentSelection}
        />
      )}

      {receiptLoading && (
        <div className="payment-receipt-loading-overlay" role="status">
          Preparando comprobante...
        </div>
      )}

      {receiptState && selectedStudent && (
        <ReceiptModal
          comprobante={receiptState.comprobante}
          estudiante={studentReceiptInfo}
          inscripciones={inscripciones}
          obligaciones={receiptState.obligaciones}
          whatsappNumber={
            preferredContact?.whatsapp ??
            preferredContact?.telefono ??
            null
          }
          whatsappContactName={preferredContact?.nombre ?? null}
          onClose={() => setReceiptState(null)}
        />
      )}
    </>
  )
}

export default PaymentsPage
