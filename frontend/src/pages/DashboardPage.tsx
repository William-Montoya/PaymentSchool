import {
  BookOpenCheck,
  CircleDollarSign,
  GraduationCap,
  TriangleAlert,
  WalletCards,
} from 'lucide-react'

import {
  useQuery,
} from '@tanstack/react-query'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  getEvaluacionesActivas,
} from '../api/evaluaciones'

import {
  getDashboardOverview,
} from '../api/reportes'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import DashboardCalendar from
  '../components/dashboard/DashboardCalendar'

import DebtByGradeChart from
  '../components/dashboard/DebtByGradeChart'

import FinancialDonut from
  '../components/dashboard/FinancialDonut'

import InsolventStudentsTable from
  '../components/dashboard/InsolventStudentsTable'

import KpiCard from
  '../components/dashboard/KpiCard'

import FullPageLoader from
  '../components/FullPageLoader'

import {
  formatCurrency,
  formatInteger,
} from '../utils/formatters'

function DashboardPage() {
  const {
    user,
    hasPermission,
  } = useAuth()

  const canViewReports =
    hasPermission(
      PERMISSIONS.REPORTES_VER,
    )

  const canViewAcademic =
    hasPermission(
      PERMISSIONS.ACADEMICO_VER,
    )

  const dashboardQuery =
    useQuery({
      queryKey: [
        'dashboard-overview',
      ],
      queryFn:
        getDashboardOverview,
      enabled:
        canViewReports,
    })

  const evaluationsQuery =
    useQuery({
      queryKey: [
        'dashboard-evaluations',
      ],
      queryFn:
        getEvaluacionesActivas,
      enabled:
        canViewAcademic,
    })

  if (!user) {
    return null
  }

  const displayName =
    user.empleado
      ?.split(' ')[0] ??
    user.username

  const todayLabel =
    new Intl.DateTimeFormat(
      'es-GT',
      {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric',
      },
    ).format(
      new Date(),
    )

  if (
    canViewReports &&
    dashboardQuery.isLoading
  ) {
    return (
      <FullPageLoader
        message="Cargando dashboard..."
      />
    )
  }

  if (!canViewReports) {
    return (
      <main className="dashboard-page">
        <header className="dashboard-hero">
          <div>
            <span className="dashboard-welcome">
              Bienvenido
            </span>

            <h1>
              Hola, {displayName}
            </h1>

            <p>
              {todayLabel}
            </p>
          </div>
        </header>

        <section className="dashboard-no-access">
          <h2>
            Resumen financiero
          </h2>

          <p>
            Su usuario no tiene el permiso
            REPORTES_VER para consultar
            los indicadores financieros
            del dashboard.
          </p>
        </section>
      </main>
    )
  }

  if (
    dashboardQuery.isError ||
    !dashboardQuery.data
  ) {
    return (
      <main className="dashboard-page">
        <section className="dashboard-load-error">
          <h2>
            No fue posible cargar
            el dashboard
          </h2>

          <p>
            {getApiErrorMessage(
              dashboardQuery.error,
              'No fue posible obtener los reportes.',
            )}
          </p>

          <button
            className="button button-primary"
            type="button"
            onClick={() => {
              void dashboardQuery.refetch()
            }}
          >
            Reintentar
          </button>
        </section>
      </main>
    )
  }

  const {
    resumen,
    deudaPorGrado,
    estudiantesInsolventes,
  } =
    dashboardQuery.data

  const evaluations =
    evaluationsQuery.data ?? []

  return (
    <main className="dashboard-page">
      <header className="dashboard-hero">
        <div>
          <span className="dashboard-welcome">
            Bienvenido
          </span>

          <h1>
            Hola, {displayName}
          </h1>

          <p>
            {todayLabel}
          </p>
        </div>

        <div className="dashboard-hero-badge">
          <span />
          Sistema actualizado
        </div>
      </header>

      <section className="kpi-grid">
        <KpiCard
          label="Estudiantes activos"
          value={
            formatInteger(
              resumen.estudiantes_activos,
            )
          }
          helper="Actualmente activos"
          icon={GraduationCap}
          tone="purple"
        />

        <KpiCard
          label="Inscripciones"
          value={
            formatInteger(
              resumen.inscripciones_activas,
            )
          }
          helper="Inscripciones activas"
          icon={BookOpenCheck}
          tone="navy"
        />

        <KpiCard
          label="Total pagado"
          value={
            formatCurrency(
              resumen.total_pagado,
            )
          }
          helper="Monto registrado"
          icon={WalletCards}
          tone="green"
        />

        <KpiCard
          label="Deuda total"
          value={
            formatCurrency(
              resumen.deuda_total,
            )
          }
          helper="Saldo pendiente"
          icon={CircleDollarSign}
          tone="orange"
        />

        <KpiCard
          label="Insolventes"
          value={
            formatInteger(
              resumen.estudiantes_insolventes,
            )
          }
          helper="Estudiantes con deuda"
          icon={TriangleAlert}
          tone="coral"
        />
      </section>

      <section className="dashboard-charts-grid">
        <DebtByGradeChart
          data={deudaPorGrado}
        />

        <FinancialDonut
          totalPagado={
            resumen.total_pagado
          }
          deudaTotal={
            resumen.deuda_total
          }
        />
      </section>

      <section className="dashboard-lower-grid">
        <InsolventStudentsTable
          students={
            estudiantesInsolventes
          }
        />

        <DashboardCalendar
          evaluations={evaluations}
          canViewAcademic={
            canViewAcademic
          }
        />
      </section>
    </main>
  )
}

export default DashboardPage