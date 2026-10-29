import {
  Route,
  Routes,
} from 'react-router-dom'

import ProtectedRoute from
  '../auth/ProtectedRoute'

import PublicOnlyRoute from
  '../auth/PublicOnlyRoute'

import RequirePermission from
  '../auth/RequirePermission'

import {
  PERMISSIONS,
} from '../auth/permissions'

import AppLayout from
  '../layouts/AppLayout'

import AccessDeniedPage from
  '../pages/AccessDeniedPage'

import AcademicPage from
  '../pages/AcademicPage'

import DashboardPage from
  '../pages/DashboardPage'

import EnrollmentsPage from
  '../pages/EnrollmentsPage'

import ExpedientesPage from
  '../pages/ExpedientesPage'

import FinancePage from
  '../pages/FinancePage'

import LoginPage from
  '../pages/LoginPage'

import PaymentsPage from
  '../pages/PaymentsPage'

import ReportsPage from
  '../pages/ReportsPage'

import NotificationsPage from
  '../pages/NotificationsPage'

import SecurityPage from
  '../pages/SecurityPage'

import AuditPage from
  '../pages/AuditPage'

import NotFoundPage from
  '../pages/NotFoundPage'

import StudentDetailPage from
  '../pages/StudentDetailPage'

import StudentsPage from
  '../pages/StudentsPage'


function AppRoutes() {
  return (
    <Routes>
      <Route
        element={
          <PublicOnlyRoute />
        }
      >
        <Route
          path="/login"
          element={
            <LoginPage />
          }
        />
      </Route>

      <Route
        element={
          <ProtectedRoute />
        }
      >
        <Route
          element={
            <AppLayout />
          }
        >
          <Route
            index
            element={
              <DashboardPage />
            }
          />

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .ESTUDIANTES_VER,
                ]}
              />
            }
          >
            <Route
              path="estudiantes"
              element={
                <StudentsPage />
              }
            />

            <Route
              path="estudiantes/:idEstudiante"
              element={
                <StudentDetailPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .EXPEDIENTES_VER,
                ]}
              />
            }
          >
            <Route
              path="expedientes"
              element={
                <ExpedientesPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .ACADEMICO_VER,
                ]}
              />
            }
          >
            <Route
              path="academico"
              element={
                <AcademicPage />
              }
            />

            <Route
              path="inscripciones"
              element={
                <EnrollmentsPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .FINANZAS_VER,
                ]}
              />
            }
          >
            <Route
              path="finanzas"
              element={
                <FinancePage />
              }
            />

            <Route
              path="pagos"
              element={
                <PaymentsPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .REPORTES_VER,
                ]}
              />
            }
          >
            <Route
              path="reportes"
              element={
                <ReportsPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .NOTIFICACIONES_VER,
                ]}
              />
            }
          >
            <Route
              path="notificaciones"
              element={
                <NotificationsPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .SEGURIDAD_VER,
                ]}
              />
            }
          >
            <Route
              path="seguridad"
              element={
                <SecurityPage />
              }
            />
          </Route>

          <Route
            element={
              <RequirePermission
                anyOf={[
                  PERMISSIONS
                    .AUDITORIA_VER,
                ]}
              />
            }
          >
            <Route
              path="auditoria"
              element={
                <AuditPage />
              }
            />
          </Route>

          <Route
            path="403"
            element={
              <AccessDeniedPage />
            }
          />

          <Route
            path="*"
            element={
              <NotFoundPage />
            }
          />
        </Route>
      </Route>
    </Routes>
  )
}


export default AppRoutes
