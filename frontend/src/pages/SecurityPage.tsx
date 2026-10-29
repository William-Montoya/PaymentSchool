import {
  BadgeCheck,
  KeyRound,
  LockKeyhole,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  UserCog,
  UsersRound,
} from 'lucide-react'

import {
  useMemo,
  useState,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  createEmpleado,
  createPermiso,
  createRol,
  createUsuario,
  getEmpleados,
  getPermisos,
  getRoles,
  getUsuarios,
  updateEmpleado,
  updateEmpleadoEstado,
  updatePermiso,
  updateRol,
  updateRolEstado,
  updateRolPermisos,
  updateUsuarioEstado,
  updateUsuarioPassword,
  updateUsuarioRoles,
} from '../api/seguridad'

import {
  getApiErrorMessage,
} from '../api/errors'

import {
  PERMISSIONS,
} from '../auth/permissions'

import {
  useAuth,
} from '../auth/useAuth'

import EmpleadoFormModal from
  '../components/security/EmpleadoFormModal'

import PasswordModal from
  '../components/security/PasswordModal'

import PermisoFormModal from
  '../components/security/PermisoFormModal'

import RolFormModal from
  '../components/security/RolFormModal'

import UsuarioFormModal from
  '../components/security/UsuarioFormModal'

import UsuarioRolesModal from
  '../components/security/UsuarioRolesModal'

import type {
  Empleado,
  EmpleadoCreate,
  EstadoUsuario,
  Permiso,
  RolDetalle,
  UsuarioCreate,
  UsuarioDetalle,
} from '../types/seguridad'

import '../styles/security.css'


type SecurityTab =
  | 'USUARIOS'
  | 'ROLES'
  | 'EMPLEADOS'
  | 'PERMISOS'


const estadoUsuarioLabels:
Record<EstadoUsuario, string> = {
  ACTIVO: 'Activo',
  INACTIVO: 'Inactivo',
  BLOQUEADO: 'Bloqueado',
}


function formatDateTime(value: string | null) {
  if (!value) {
    return 'Nunca'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    },
  ).format(date)
}


function SecurityPage() {
  const queryClient = useQueryClient()

  const {
    hasAnyPermission,
  } = useAuth()

  const canManage = hasAnyPermission([
    PERMISSIONS.SEGURIDAD_GESTIONAR,
  ])

  const [tab, setTab] = useState<SecurityTab>('USUARIOS')
  const [search, setSearch] = useState('')

  const [employeeModalOpen, setEmployeeModalOpen] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Empleado | null>(null)

  const [userModalOpen, setUserModalOpen] = useState(false)
  const [rolesUser, setRolesUser] = useState<UsuarioDetalle | null>(null)
  const [passwordUser, setPasswordUser] = useState<UsuarioDetalle | null>(null)

  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<RolDetalle | null>(null)

  const [permissionModalOpen, setPermissionModalOpen] = useState(false)
  const [selectedPermission, setSelectedPermission] = useState<Permiso | null>(null)

  const empleadosQuery = useQuery({
    queryKey: ['seguridad-empleados'],
    queryFn: () => getEmpleados(),
  })

  const usuariosQuery = useQuery({
    queryKey: ['seguridad-usuarios'],
    queryFn: () => getUsuarios(),
  })

  const rolesQuery = useQuery({
    queryKey: ['seguridad-roles'],
    queryFn: () => getRoles(),
  })

  const permisosQuery = useQuery({
    queryKey: ['seguridad-permisos'],
    queryFn: getPermisos,
  })

  const empleados = empleadosQuery.data ?? []
  const usuarios = usuariosQuery.data ?? []
  const roles = rolesQuery.data ?? []
  const permisos = permisosQuery.data ?? []

  const empleadosSinUsuario = useMemo(
    () => {
      const empleadosConUsuario = new Set(
        usuarios
          .map((usuario) => usuario.id_empleado)
          .filter((id): id is number => id !== null),
      )

      return empleados.filter(
        (empleado) =>
          empleado.activo &&
          !empleadosConUsuario.has(empleado.id_empleado),
      )
    },
    [empleados, usuarios],
  )

  const normalizedSearch = search.trim().toLowerCase()

  const filteredUsers = useMemo(
    () => usuarios.filter((usuario) => {
      if (!normalizedSearch) {
        return true
      }

      return [
        usuario.username,
        usuario.empleado ?? '',
        usuario.cargo ?? '',
        usuario.estado,
        ...usuario.roles.map((rol) => rol.nombre),
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedSearch)
    }),
    [usuarios, normalizedSearch],
  )

  const filteredRoles = useMemo(
    () => roles.filter((rol) => {
      if (!normalizedSearch) {
        return true
      }

      return [
        rol.nombre,
        rol.descripcion ?? '',
        ...rol.permisos.map((permiso) => permiso.nombre),
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedSearch)
    }),
    [roles, normalizedSearch],
  )

  const filteredEmployees = useMemo(
    () => empleados.filter((empleado) => {
      if (!normalizedSearch) {
        return true
      }

      return [
        empleado.nombres,
        empleado.apellidos,
        empleado.cargo ?? '',
        empleado.email ?? '',
        empleado.telefono ?? '',
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedSearch)
    }),
    [empleados, normalizedSearch],
  )

  const filteredPermissions = useMemo(
    () => permisos.filter((permiso) => {
      if (!normalizedSearch) {
        return true
      }

      return [
        permiso.nombre,
        permiso.descripcion ?? '',
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedSearch)
    }),
    [permisos, normalizedSearch],
  )

  const invalidateSecurity = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['seguridad-empleados'] }),
      queryClient.invalidateQueries({ queryKey: ['seguridad-usuarios'] }),
      queryClient.invalidateQueries({ queryKey: ['seguridad-roles'] }),
      queryClient.invalidateQueries({ queryKey: ['seguridad-permisos'] }),
    ])
  }

  const employeeSaveMutation = useMutation({
    mutationFn: async (payload: EmpleadoCreate) => {
      if (selectedEmployee) {
        return updateEmpleado(
          selectedEmployee.id_empleado,
          payload,
        )
      }

      return createEmpleado(payload)
    },
    onSuccess: async () => {
      await invalidateSecurity()
      setEmployeeModalOpen(false)
      setSelectedEmployee(null)
    },
  })

  const employeeStateMutation = useMutation({
    mutationFn: ({
      empleado,
      activo,
    }: {
      empleado: Empleado
      activo: boolean
    }) => updateEmpleadoEstado(
      empleado.id_empleado,
      activo,
    ),
    onSuccess: invalidateSecurity,
  })

  const userCreateMutation = useMutation({
    mutationFn: (payload: UsuarioCreate) => createUsuario(payload),
    onSuccess: async () => {
      await invalidateSecurity()
      setUserModalOpen(false)
    },
  })

  const userRolesMutation = useMutation({
    mutationFn: ({
      idUsuario,
      idsRol,
    }: {
      idUsuario: number
      idsRol: number[]
    }) => updateUsuarioRoles(idUsuario, idsRol),
    onSuccess: async () => {
      await invalidateSecurity()
      setRolesUser(null)
    },
  })

  const userPasswordMutation = useMutation({
    mutationFn: ({
      idUsuario,
      password,
    }: {
      idUsuario: number
      password: string
    }) => updateUsuarioPassword(idUsuario, password),
    onSuccess: async () => {
      await invalidateSecurity()
      setPasswordUser(null)
    },
  })

  const userStateMutation = useMutation({
    mutationFn: ({
      idUsuario,
      estado,
    }: {
      idUsuario: number
      estado: EstadoUsuario
    }) => updateUsuarioEstado(idUsuario, estado),
    onSuccess: invalidateSecurity,
  })

  const roleSaveMutation = useMutation({
    mutationFn: async (payload: {
      nombre: string
      descripcion: string | null
      idsPermiso: number[]
    }) => {
      if (selectedRole) {
        await updateRol(
          selectedRole.id_rol,
          {
            descripcion: payload.descripcion,
          },
        )

        return updateRolPermisos(
          selectedRole.id_rol,
          payload.idsPermiso,
        )
      }

      const created = await createRol({
        nombre: payload.nombre,
        descripcion: payload.descripcion,
      })

      return updateRolPermisos(
        created.id_rol,
        payload.idsPermiso,
      )
    },
    onSuccess: async () => {
      await invalidateSecurity()
      setRoleModalOpen(false)
      setSelectedRole(null)
    },
  })

  const roleStateMutation = useMutation({
    mutationFn: ({
      idRol,
      activo,
    }: {
      idRol: number
      activo: boolean
    }) => updateRolEstado(idRol, activo),
    onSuccess: invalidateSecurity,
  })

  const permissionSaveMutation = useMutation({
    mutationFn: async ({
      nombre,
      descripcion,
    }: {
      nombre: string
      descripcion: string | null
    }) => {
      if (selectedPermission) {
        return updatePermiso(
          selectedPermission.id_permiso,
          {
            descripcion,
          },
        )
      }

      return createPermiso({
        nombre,
        descripcion,
      })
    },
    onSuccess: async () => {
      await invalidateSecurity()
      setPermissionModalOpen(false)
      setSelectedPermission(null)
    },
  })

  const queryError =
    empleadosQuery.isError ||
    usuariosQuery.isError ||
    rolesQuery.isError ||
    permisosQuery.isError

  const queryLoading =
    empleadosQuery.isLoading ||
    usuariosQuery.isLoading ||
    rolesQuery.isLoading ||
    permisosQuery.isLoading

  function openNewEmployee() {
    employeeSaveMutation.reset()
    setSelectedEmployee(null)
    setEmployeeModalOpen(true)
  }

  function openEditEmployee(empleado: Empleado) {
    employeeSaveMutation.reset()
    setSelectedEmployee(empleado)
    setEmployeeModalOpen(true)
  }

  function openNewRole() {
    roleSaveMutation.reset()
    setSelectedRole(null)
    setRoleModalOpen(true)
  }

  function openEditRole(rol: RolDetalle) {
    roleSaveMutation.reset()
    setSelectedRole(rol)
    setRoleModalOpen(true)
  }

  function openNewPermission() {
    permissionSaveMutation.reset()
    setSelectedPermission(null)
    setPermissionModalOpen(true)
  }

  function openEditPermission(permiso: Permiso) {
    permissionSaveMutation.reset()
    setSelectedPermission(permiso)
    setPermissionModalOpen(true)
  }

  return (
    <>
      <main className="security-page">
        <header className="security-header">
          <div>
            <span className="dashboard-card-eyebrow">
              Administración
            </span>
            <h1>Seguridad</h1>
            <p>
              Gestión de usuarios, roles, permisos y personal administrativo.
            </p>
          </div>

          <div className="security-header-icon">
            <ShieldCheck size={28} aria-hidden="true" />
          </div>
        </header>

        <section className="security-tabs" aria-label="Módulos de seguridad">
          <button
            type="button"
            className={tab === 'USUARIOS' ? 'security-tab active' : 'security-tab'}
            onClick={() => setTab('USUARIOS')}
          >
            <UserCog size={17} aria-hidden="true" />
            Usuarios
          </button>

          <button
            type="button"
            className={tab === 'ROLES' ? 'security-tab active' : 'security-tab'}
            onClick={() => setTab('ROLES')}
          >
            <UsersRound size={17} aria-hidden="true" />
            Roles
          </button>

          <button
            type="button"
            className={tab === 'EMPLEADOS' ? 'security-tab active' : 'security-tab'}
            onClick={() => setTab('EMPLEADOS')}
          >
            <BadgeCheck size={17} aria-hidden="true" />
            Empleados
          </button>

          <button
            type="button"
            className={tab === 'PERMISOS' ? 'security-tab active' : 'security-tab'}
            onClick={() => setTab('PERMISOS')}
          >
            <LockKeyhole size={17} aria-hidden="true" />
            Permisos
          </button>
        </section>

        <section className="security-card">
          <div className="security-toolbar">
            <div className="security-search">
              <Search size={17} aria-hidden="true" />
              <input
                type="search"
                value={search}
                placeholder="Buscar..."
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>

            {canManage && tab === 'USUARIOS' && (
              <button
                className="button button-primary"
                type="button"
                onClick={() => {
                  userCreateMutation.reset()
                  setUserModalOpen(true)
                }}
              >
                <Plus size={16} aria-hidden="true" />
                Nuevo usuario
              </button>
            )}

            {canManage && tab === 'ROLES' && (
              <button
                className="button button-primary"
                type="button"
                onClick={openNewRole}
              >
                <Plus size={16} aria-hidden="true" />
                Nuevo rol
              </button>
            )}

            {canManage && tab === 'EMPLEADOS' && (
              <button
                className="button button-primary"
                type="button"
                onClick={openNewEmployee}
              >
                <Plus size={16} aria-hidden="true" />
                Nuevo empleado
              </button>
            )}

            {canManage && tab === 'PERMISOS' && (
              <button
                className="button button-primary"
                type="button"
                onClick={openNewPermission}
              >
                <Plus size={16} aria-hidden="true" />
                Nuevo permiso
              </button>
            )}
          </div>

          {queryLoading ? (
            <div className="security-empty">Cargando seguridad...</div>
          ) : queryError ? (
            <div className="security-error-panel">
              <strong>No fue posible cargar Seguridad.</strong>
              <p>
                {getApiErrorMessage(
                  empleadosQuery.error ||
                    usuariosQuery.error ||
                    rolesQuery.error ||
                    permisosQuery.error,
                  'No fue posible obtener los catálogos de seguridad.',
                )}
              </p>
              <button
                className="button button-secondary"
                type="button"
                onClick={() => {
                  void invalidateSecurity()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : tab === 'USUARIOS' ? (
            <div className="security-table-wrapper">
              <table className="security-table">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Empleado / Cargo</th>
                    <th>Roles</th>
                    <th>Estado</th>
                    <th>Último acceso</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((usuario) => (
                    <tr key={usuario.id_usuario}>
                      <td>
                        <strong>{usuario.username}</strong>
                        <small>#{usuario.id_usuario}</small>
                      </td>
                      <td>
                        <strong>{usuario.empleado ?? 'Sin empleado'}</strong>
                        <small>{usuario.cargo ?? 'Sin cargo'}</small>
                      </td>
                      <td>
                        <div className="security-chip-list">
                          {usuario.roles.map((rol) => (
                            <span key={rol.id_rol}>{rol.nombre}</span>
                          ))}
                        </div>
                      </td>
                      <td>
                        {canManage ? (
                          <select
                            className="security-inline-select"
                            value={usuario.estado}
                            disabled={userStateMutation.isPending}
                            onChange={(event) => {
                              userStateMutation.mutate({
                                idUsuario: usuario.id_usuario,
                                estado: event.target.value as EstadoUsuario,
                              })
                            }}
                          >
                            {Object.entries(estadoUsuarioLabels).map(
                              ([value, label]) => (
                                <option key={value} value={value}>
                                  {label}
                                </option>
                              ),
                            )}
                          </select>
                        ) : (
                          <span className={`security-status security-status-${usuario.estado.toLowerCase()}`}>
                            {estadoUsuarioLabels[usuario.estado]}
                          </span>
                        )}
                      </td>
                      <td>{formatDateTime(usuario.ultimo_acceso)}</td>
                      <td>
                        {canManage && (
                          <div className="security-actions">
                            <button
                              type="button"
                              title="Administrar roles"
                              onClick={() => {
                                userRolesMutation.reset()
                                setRolesUser(usuario)
                              }}
                            >
                              <UsersRound size={16} aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              title="Cambiar contraseña"
                              onClick={() => {
                                userPasswordMutation.reset()
                                setPasswordUser(usuario)
                              }}
                            >
                              <KeyRound size={16} aria-hidden="true" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredUsers.length === 0 && (
                <div className="security-empty">No hay usuarios para mostrar.</div>
              )}
            </div>
          ) : tab === 'ROLES' ? (
            <div className="security-table-wrapper">
              <table className="security-table">
                <thead>
                  <tr>
                    <th>Rol</th>
                    <th>Descripción</th>
                    <th>Permisos</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRoles.map((rol) => (
                    <tr key={rol.id_rol}>
                      <td><strong>{rol.nombre}</strong></td>
                      <td>{rol.descripcion ?? '—'}</td>
                      <td>
                        <div className="security-chip-list">
                          {rol.permisos.slice(0, 5).map((permiso) => (
                            <span key={permiso.id_permiso}>{permiso.nombre}</span>
                          ))}
                          {rol.permisos.length > 5 && (
                            <span>+{rol.permisos.length - 5}</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className={`security-status ${rol.activo ? 'security-status-activo' : 'security-status-inactivo'}`}>
                          {rol.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        {canManage && (
                          <div className="security-actions">
                            <button
                              type="button"
                              title="Editar rol"
                              onClick={() => openEditRole(rol)}
                            >
                              <Pencil size={16} aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              title={rol.activo ? 'Desactivar rol' : 'Activar rol'}
                              disabled={roleStateMutation.isPending}
                              onClick={() => roleStateMutation.mutate({
                                idRol: rol.id_rol,
                                activo: !rol.activo,
                              })}
                            >
                              <ShieldCheck size={16} aria-hidden="true" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredRoles.length === 0 && (
                <div className="security-empty">No hay roles para mostrar.</div>
              )}
            </div>
          ) : tab === 'EMPLEADOS' ? (
            <div className="security-table-wrapper">
              <table className="security-table">
                <thead>
                  <tr>
                    <th>Empleado</th>
                    <th>Cargo</th>
                    <th>Contacto</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEmployees.map((empleado) => (
                    <tr key={empleado.id_empleado}>
                      <td>
                        <strong>{empleado.nombres} {empleado.apellidos}</strong>
                        <small>#{empleado.id_empleado}</small>
                      </td>
                      <td>{empleado.cargo ?? '—'}</td>
                      <td>
                        <strong>{empleado.email ?? 'Sin correo'}</strong>
                        <small>{empleado.telefono ?? 'Sin teléfono'}</small>
                      </td>
                      <td>
                        <span className={`security-status ${empleado.activo ? 'security-status-activo' : 'security-status-inactivo'}`}>
                          {empleado.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        {canManage && (
                          <div className="security-actions">
                            <button
                              type="button"
                              title="Editar empleado"
                              onClick={() => openEditEmployee(empleado)}
                            >
                              <Pencil size={16} aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              title={empleado.activo ? 'Desactivar empleado' : 'Activar empleado'}
                              disabled={employeeStateMutation.isPending}
                              onClick={() => employeeStateMutation.mutate({
                                empleado,
                                activo: !empleado.activo,
                              })}
                            >
                              <BadgeCheck size={16} aria-hidden="true" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredEmployees.length === 0 && (
                <div className="security-empty">No hay empleados para mostrar.</div>
              )}
            </div>
          ) : (
            <div className="security-table-wrapper">
              <table className="security-table">
                <thead>
                  <tr>
                    <th>Permiso</th>
                    <th>Descripción</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPermissions.map((permiso) => (
                    <tr key={permiso.id_permiso}>
                      <td><strong>{permiso.nombre}</strong></td>
                      <td>{permiso.descripcion ?? '—'}</td>
                      <td>
                        {canManage && (
                          <div className="security-actions">
                            <button
                              type="button"
                              title="Editar permiso"
                              onClick={() => openEditPermission(permiso)}
                            >
                              <Pencil size={16} aria-hidden="true" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredPermissions.length === 0 && (
                <div className="security-empty">No hay permisos para mostrar.</div>
              )}
            </div>
          )}
        </section>
      </main>

      {employeeModalOpen && (
        <EmpleadoFormModal
          empleado={selectedEmployee}
          isSubmitting={employeeSaveMutation.isPending}
          error={
            employeeSaveMutation.isError
              ? getApiErrorMessage(
                  employeeSaveMutation.error,
                  'No fue posible guardar el empleado.',
                )
              : null
          }
          onClose={() => {
            if (!employeeSaveMutation.isPending) {
              setEmployeeModalOpen(false)
              setSelectedEmployee(null)
            }
          }}
          onSubmit={async (payload) => {
            await employeeSaveMutation.mutateAsync(payload)
          }}
        />
      )}

      {userModalOpen && (
        <UsuarioFormModal
          empleados={empleadosSinUsuario}
          roles={roles}
          isSubmitting={userCreateMutation.isPending}
          error={
            userCreateMutation.isError
              ? getApiErrorMessage(
                  userCreateMutation.error,
                  'No fue posible crear el usuario.',
                )
              : null
          }
          onClose={() => {
            if (!userCreateMutation.isPending) {
              setUserModalOpen(false)
            }
          }}
          onSubmit={async (payload) => {
            await userCreateMutation.mutateAsync(payload)
          }}
        />
      )}

      {rolesUser && (
        <UsuarioRolesModal
          usuario={rolesUser}
          roles={roles}
          isSubmitting={userRolesMutation.isPending}
          error={
            userRolesMutation.isError
              ? getApiErrorMessage(
                  userRolesMutation.error,
                  'No fue posible actualizar los roles.',
                )
              : null
          }
          onClose={() => {
            if (!userRolesMutation.isPending) {
              setRolesUser(null)
            }
          }}
          onSubmit={async (idsRol) => {
            await userRolesMutation.mutateAsync({
              idUsuario: rolesUser.id_usuario,
              idsRol,
            })
          }}
        />
      )}

      {passwordUser && (
        <PasswordModal
          username={passwordUser.username}
          isSubmitting={userPasswordMutation.isPending}
          error={
            userPasswordMutation.isError
              ? getApiErrorMessage(
                  userPasswordMutation.error,
                  'No fue posible cambiar la contraseña.',
                )
              : null
          }
          onClose={() => {
            if (!userPasswordMutation.isPending) {
              setPasswordUser(null)
            }
          }}
          onSubmit={async (password) => {
            await userPasswordMutation.mutateAsync({
              idUsuario: passwordUser.id_usuario,
              password,
            })
          }}
        />
      )}

      {roleModalOpen && (
        <RolFormModal
          rol={selectedRole}
          permisos={permisos}
          isSubmitting={roleSaveMutation.isPending}
          error={
            roleSaveMutation.isError
              ? getApiErrorMessage(
                  roleSaveMutation.error,
                  'No fue posible guardar el rol.',
                )
              : null
          }
          onClose={() => {
            if (!roleSaveMutation.isPending) {
              setRoleModalOpen(false)
              setSelectedRole(null)
            }
          }}
          onSubmit={async (payload) => {
            await roleSaveMutation.mutateAsync(payload)
          }}
        />
      )}

      {permissionModalOpen && (
        <PermisoFormModal
          permiso={selectedPermission}
          isSubmitting={permissionSaveMutation.isPending}
          error={
            permissionSaveMutation.isError
              ? getApiErrorMessage(
                  permissionSaveMutation.error,
                  'No fue posible guardar el permiso.',
                )
              : null
          }
          onClose={() => {
            if (!permissionSaveMutation.isPending) {
              setPermissionModalOpen(false)
              setSelectedPermission(null)
            }
          }}
          onSubmit={async (nombre, descripcion) => {
            await permissionSaveMutation.mutateAsync({
              nombre,
              descripcion,
            })
          }}
        />
      )}
    </>
  )
}


export default SecurityPage
