import {
  BookOpenCheck,
  Check,
  Printer,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  FileText,
  FolderOpen,
  Pencil,
  Search,
  UserPlus,
  UserRound,
  UsersRound,
} from 'lucide-react'

import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import {
  getCarreraCiclos,
  getCarreras,
  getCiclos,
  getGrados,
} from '../../api/catalogoAcademico'

import {
  getApiErrorMessage,
} from '../../api/errors'

import {
  createEstudiante,
  getEstudiantes,
  updateEstudiante,
} from '../../api/estudiantes'

import {
  createInscripcion,
} from '../../api/inscripciones'

import {
  PERMISSIONS,
} from '../../auth/permissions'

import PermissionGate from
  '../../auth/PermissionGate'

import EstudianteFormModal from
  '../estudiantes/EstudianteFormModal'

import type {
  Contacto,
} from '../../types/contacto'

import type {
  Estudiante,
  EstudianteCreate,
} from '../../types/estudiante'

import type {
  ExpedienteSummary,
} from '../../types/expediente'

import type {
  InscripcionDetalle,
  TipoInscripcion,
} from '../../types/inscripcion'

import ContactosStep from
  './ContactosStep'

import ExpedienteChecklist from
  './ExpedienteChecklist'

import {
  printInscripcionComprobante,
} from '../../utils/printInscripcion'

import '../../styles/enrollment-wizard-extra.css'


interface InscripcionWizardProps {
  onClose: () => void
}


type StudentOrigin =
  | 'EXISTENTE'
  | 'NUEVO'
  | null


const steps = [
  {
    id: 1,
    label: 'Estudiante',
    icon: UserRound,
  },
  {
    id: 2,
    label: 'Datos',
    icon: FileText,
  },
  {
    id: 3,
    label: 'Oferta académica',
    icon: BookOpenCheck,
  },
  {
    id: 4,
    label: 'Expediente',
    icon: FolderOpen,
  },
  {
    id: 5,
    label: 'Encargado',
    icon: UsersRound,
  },
  {
    id: 6,
    label: 'Confirmar',
    icon: ClipboardCheck,
  },
] as const


const tipoLabels:
Record<TipoInscripcion, string> = {
  NUEVA:
    'Nueva inscripción',

  REINSCRIPCION:
    'Reinscripción',

  TRASLADO:
    'Traslado',
}


function displayValue(
  value:
    string |
    null |
    undefined,
) {
  return value?.trim()
    ? value
    : 'No registrado'
}


function displayDate(
  value:
    string |
    null |
    undefined,
) {
  if (!value) {
    return 'No registrada'
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


function InscripcionWizard({
  onClose,
}: InscripcionWizardProps) {
  const queryClient =
    useQueryClient()

  const [
    step,
    setStep,
  ] = useState(1)

  const [
    searchDraft,
    setSearchDraft,
  ] = useState('')

  const [
    search,
    setSearch,
  ] = useState('')

  const [
    selectedStudent,
    setSelectedStudent,
  ] = useState<
    Estudiante |
    null
  >(null)

  const [
    studentOrigin,
    setStudentOrigin,
  ] = useState<StudentOrigin>(
    null,
  )

  const [
    showStudentForm,
    setShowStudentForm,
  ] = useState(false)

  const [
    editingStudent,
    setEditingStudent,
  ] = useState(false)

  const [
    selectedCicloId,
    setSelectedCicloId,
  ] = useState<number | null>(
    null,
  )

  const [
    selectedCarreraCicloId,
    setSelectedCarreraCicloId,
  ] = useState<number | null>(
    null,
  )

  const [
    selectedGradoId,
    setSelectedGradoId,
  ] = useState<number | null>(
    null,
  )

  const [
    tipo,
    setTipo,
  ] = useState<TipoInscripcion>(
    'NUEVA',
  )

  const [
    observaciones,
    setObservaciones,
  ] = useState('')

  const [
    expedienteSummary,
    setExpedienteSummary,
  ] = useState<
    ExpedienteSummary |
    null
  >(null)

  const [
    contactos,
    setContactos,
  ] = useState<Contacto[]>(
    [],
  )

  const [
    completed,
    setCompleted,
  ] = useState<
    InscripcionDetalle |
    null
  >(null)

  const studentsQuery =
    useQuery({
      queryKey: [
        'estudiantes-inscripcion',
        search,
      ],

      queryFn: () =>
        getEstudiantes({
          offset: 0,
          limit: 20,
          estado: 'ACTIVO',
          buscar:
            search ||
            undefined,
        }),
    })

  const ciclosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'ciclos',
      ],

      queryFn:
        getCiclos,
    })

  const carrerasQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'carreras',
      ],

      queryFn:
        getCarreras,
    })

  const carreraCiclosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'carrera-ciclos',
        selectedCicloId,
      ],

      queryFn: () =>
        getCarreraCiclos({
          id_ciclo:
            selectedCicloId ??
            undefined,
        }),

      enabled:
        selectedCicloId !== null,
    })

  const gradosQuery =
    useQuery({
      queryKey: [
        'catalogo-academico',
        'grados',
        selectedCarreraCicloId,
      ],

      queryFn: () =>
        getGrados({
          id_carrera_ciclo:
            selectedCarreraCicloId ??
            undefined,
        }),

      enabled:
        selectedCarreraCicloId !== null,
    })

  const createStudentMutation =
    useMutation({
      mutationFn:
        createEstudiante,

      onSuccess: async (
        estudiante,
      ) => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'estudiantes-inscripcion',
            ],
          })

        selectStudent(
          estudiante,
          'NUEVO',
        )

        setTipo(
          'NUEVA',
        )

        setShowStudentForm(
          false,
        )

        setEditingStudent(
          false,
        )

        setStep(2)

      },
    })

  const updateStudentMutation =
    useMutation({
      mutationFn: (
        payload:
          EstudianteCreate,
      ) => {
        if (!selectedStudent) {
          throw new Error(
            'Estudiante no seleccionado',
          )
        }

        return updateEstudiante(
          selectedStudent
            .id_estudiante,

          payload,
        )
      },

      onSuccess: async (
        estudiante,
      ) => {
        await Promise.all([
          queryClient
            .invalidateQueries({
              queryKey: [
                'estudiantes-inscripcion',
              ],
            }),

          queryClient
            .invalidateQueries({
              queryKey: [
                'estudiante',
                estudiante
                  .id_estudiante,
              ],
            }),
        ])

        setSelectedStudent(
          estudiante,
        )

        setShowStudentForm(
          false,
        )

        setEditingStudent(
          false,
        )
      },
    })

  const createInscripcionMutation =
    useMutation({
      mutationFn:
        createInscripcion,

      onSuccess: async (
        inscripcion,
      ) => {
        await queryClient
          .invalidateQueries({
            queryKey: [
              'inscripciones',
            ],
          })

        setCompleted(
          inscripcion,
        )
      },
    })

  const students =
    studentsQuery.data ?? []

  const ciclos =
    (ciclosQuery.data ?? [])
      .filter(
        (ciclo) =>
          ciclo.estado !==
          'CERRADO',
      )

  const carreras =
    carrerasQuery.data ?? []

  const carreraCiclos =
    (
      carreraCiclosQuery
        .data ?? []
    ).filter(
      (item) =>
        item.estado,
    )

  const grados =
    (
      gradosQuery.data ?? []
    ).filter(
      (grado) =>
        grado.activo,
    )

  const carrerasPorId =
    useMemo(
      () =>
        new Map(
          carreras.map(
            (carrera) => [
              carrera.id_carrera,
              carrera,
            ],
          ),
        ),
      [carreras],
    )

  const selectedCiclo =
    ciclos.find(
      (item) =>
        item.id_ciclo ===
        selectedCicloId,
    ) ?? null

  const selectedCarreraCiclo =
    carreraCiclos.find(
      (item) =>
        item.id_carrera_ciclo ===
        selectedCarreraCicloId,
    ) ?? null

  const selectedCarrera =
    selectedCarreraCiclo
      ? (
        carrerasPorId.get(
          selectedCarreraCiclo
            .id_carrera,
        ) ?? null
      )
      : null

  const selectedGrado =
    grados.find(
      (item) =>
        item.id_grado ===
        selectedGradoId,
    ) ?? null

  const selectedCarreraNombre =
    selectedCarreraCiclo
      ? (
        selectedCarreraCiclo
          .nombre_comercial ||
        selectedCarrera
          ?.nombre ||
        (
          'Carrera #' +
          selectedCarreraCiclo
            .id_carrera
        )
      )
      : ''

  const contactoPrincipal =
    contactos.find(
      (contacto) =>
        contacto.es_principal,
    ) ?? null

  function resetStudentDependentData() {
    setSelectedCicloId(
      null,
    )

    setSelectedCarreraCicloId(
      null,
    )

    setSelectedGradoId(
      null,
    )

    setObservaciones('')

    setExpedienteSummary(
      null,
    )

    setContactos([])
  }

  function selectStudent(
    student: Estudiante,
    origin:
      Exclude<
        StudentOrigin,
        null
      >,
  ) {
    setSelectedStudent(
      student,
    )

    setStudentOrigin(
      origin,
    )

    setTipo(
      origin === 'EXISTENTE'
        ? 'REINSCRIPCION'
        : 'NUEVA',
    )

    resetStudentDependentData()
  }

  function handleSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setSearch(
      searchDraft.trim(),
    )
  }

  function openCreateStudent() {
    createStudentMutation.reset()
    updateStudentMutation.reset()

    setEditingStudent(
      false,
    )

    setShowStudentForm(
      true,
    )
  }

  function openEditStudent() {
    if (!selectedStudent) {
      return
    }

    createStudentMutation.reset()
    updateStudentMutation.reset()

    setEditingStudent(
      true,
    )

    setShowStudentForm(
      true,
    )
  }

  function closeStudentForm() {
    if (
      createStudentMutation
        .isPending ||
      updateStudentMutation
        .isPending
    ) {
      return
    }

    createStudentMutation.reset()
    updateStudentMutation.reset()

    setShowStudentForm(
      false,
    )

    setEditingStudent(
      false,
    )
  }

  async function handleStudentSubmit(
    payload:
      EstudianteCreate,
  ) {
    if (editingStudent) {
      await updateStudentMutation
        .mutateAsync(
          payload,
        )

      return
    }

    await createStudentMutation
      .mutateAsync(
        payload,
      )
  }

  function handleCicloChange(
    value: string,
  ) {
    setSelectedCicloId(
      value
        ? Number(value)
        : null,
    )

    setSelectedCarreraCicloId(
      null,
    )

    setSelectedGradoId(
      null,
    )
  }

  function handleCarreraChange(
    value: string,
  ) {
    setSelectedCarreraCicloId(
      value
        ? Number(value)
        : null,
    )

    setSelectedGradoId(
      null,
    )
  }

  function canContinue() {
    if (step === 1) {
      return Boolean(
        selectedStudent,
      )
    }

    if (step === 2) {
      return Boolean(
        selectedStudent,
      )
    }

    if (step === 3) {
      return Boolean(
        selectedCicloId &&
        selectedCarreraCicloId &&
        selectedGradoId,
      )
    }

    return true
  }

  function handleNext() {
    if (
      !canContinue() ||
      step >= 6
    ) {
      return
    }

    setStep(
      (current) =>
        current + 1,
    )
  }

  function handlePrevious() {
    if (step <= 1) {
      return
    }

    setStep(
      (current) =>
        current - 1,
    )
  }

  async function handleSubmit() {
    if (
      !selectedStudent ||
      !selectedCarreraCicloId ||
      !selectedGradoId
    ) {
      return
    }

    await createInscripcionMutation
      .mutateAsync({
        id_estudiante:
          selectedStudent
            .id_estudiante,

        id_carrera_ciclo:
          selectedCarreraCicloId,

        id_grado:
          selectedGradoId,

        tipo,

        observaciones:
          observaciones
            .trim() ||
          null,
      })
  }

  if (completed) {
    return (
      <section className="module-card enrollment-wizard enrollment-success">
        <CheckCircle2
          size={48}
          aria-hidden="true"
        />

        <span className="dashboard-card-eyebrow">
          Inscripción completada
        </span>

        <h2>
          Inscripción registrada
        </h2>

        <p>
          La inscripción fue registrada
          correctamente.
        </p>

        <div className="enrollment-success-summary">
          <div>
            <span>
              Código / Carnet
            </span>

            <strong>
              {
                completed
                  .codigo_estudiante
              }
            </strong>
          </div>

          <div>
            <span>
              Estudiante
            </span>

            <strong>
              {completed.estudiante}
            </strong>
          </div>

          <div>
            <span>
              Ciclo
            </span>

            <strong>
              {completed.ciclo}
            </strong>
          </div>

          <div>
            <span>
              Carrera
            </span>

            <strong>
              {completed.carrera}
            </strong>
          </div>

          <div>
            <span>
              Grado
            </span>

            <strong>
              {completed.grado}
            </strong>
          </div>

          <div>
            <span>
              Tipo
            </span>

            <strong>
              {tipoLabels[
                completed.tipo
              ]}
            </strong>
          </div>
        </div>

        <div className="enrollment-success-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={() =>
              printInscripcionComprobante({
                inscripcion:
                  completed,

                estudiante:
                  selectedStudent,

                contactoPrincipal,
              })
            }
          >
            <Printer
              size={16}
              aria-hidden="true"
            />

            Imprimir comprobante
          </button>

          <button
            className="button button-primary"
            type="button"
            onClick={onClose}
          >
            Volver a inscripciones
          </button>
        </div>
      </section>
    )
  }

  return (
    <>
      <section className="module-card enrollment-wizard">
        <div className="enrollment-steps">
          {steps.map(
            (item) => {
              const Icon =
                item.icon

              const isActive =
                item.id === step

              const isComplete =
                item.id < step

              return (
                <div
                  className={
                    (
                      'enrollment-step ' +
                      (
                        isActive
                          ? 'enrollment-step-active'
                          : ''
                      ) +
                      (
                        isComplete
                          ? ' enrollment-step-complete'
                          : ''
                      )
                    )
                  }
                  key={item.id}
                >
                  <span className="enrollment-step-circle">
                    {isComplete ? (
                      <Check
                        size={16}
                        aria-hidden="true"
                      />
                    ) : (
                      <Icon
                        size={16}
                        aria-hidden="true"
                      />
                    )}
                  </span>

                  <strong>
                    {item.label}
                  </strong>
                </div>
              )
            },
          )}
        </div>

        <div className="enrollment-step-content">
          {step === 1 && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 1
                  </span>

                  <h2>
                    Estudiante
                  </h2>

                  <p>
                    Busca un estudiante
                    existente o regístralo
                    sin salir del proceso
                    de inscripción.
                  </p>
                </div>
              </header>

              <div className="enrollment-student-toolbar">
                <form
                  className="enrollment-search"
                  onSubmit={handleSearch}
                >
                  <Search
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    type="search"
                    value={searchDraft}
                    placeholder={
                      (
                        'Buscar por código, ' +
                        'nombre o apellido...'
                      )
                    }
                    onChange={(event) =>
                      setSearchDraft(
                        event.target.value,
                      )
                    }
                  />

                  <button type="submit">
                    Buscar
                  </button>
                </form>

                <PermissionGate
                  anyOf={[
                    PERMISSIONS
                      .ESTUDIANTES_GESTIONAR,
                  ]}
                >
                  <button
                    className="button button-primary"
                    type="button"
                    onClick={
                      openCreateStudent
                    }
                  >
                    <UserPlus
                      size={16}
                      aria-hidden="true"
                    />

                    Registrar estudiante
                  </button>
                </PermissionGate>
              </div>

              {selectedStudent && (
                <div className="selected-student-banner">
                  <CheckCircle2
                    size={20}
                    aria-hidden="true"
                  />

                  <div>
                    <strong>
                      {selectedStudent.nombres}
                      {' '}
                      {selectedStudent.apellidos}
                    </strong>

                    <span>
                      {
                        selectedStudent
                          .codigo_estudiante
                      }
                      {' · '}
                      {studentOrigin ===
                      'EXISTENTE'
                        ? (
                          'Estudiante existente · ' +
                          'Reinscripción seleccionada'
                        )
                        : (
                          'Estudiante creado en ' +
                          'este proceso'
                        )}
                    </span>
                  </div>
                </div>
              )}

              {studentsQuery.isError ? (
                <div className="module-message module-message-error">
                  {getApiErrorMessage(
                    studentsQuery.error,
                    (
                      'No fue posible cargar ' +
                      'los estudiantes.'
                    ),
                  )}
                </div>
              ) : studentsQuery.isLoading ? (
                <div className="module-message">
                  Cargando estudiantes...
                </div>
              ) : students.length === 0 ? (
                <div className="enrollment-empty-card">
                  <UserRound
                    size={36}
                    aria-hidden="true"
                  />

                  <strong>
                    No se encontraron estudiantes
                  </strong>

                  <p>
                    Puedes registrar un estudiante
                    nuevo desde esta misma
                    inscripción.
                  </p>
                </div>
              ) : (
                <div className="enrollment-student-grid">
                  {students.map(
                    (student) => {
                      const selected =
                        selectedStudent
                          ?.id_estudiante ===
                        student.id_estudiante

                      return (
                        <button
                          key={
                            student
                              .id_estudiante
                          }
                          className={
                            (
                              'enrollment-student-card ' +
                              (
                                selected
                                  ? 'enrollment-student-card-selected'
                                  : ''
                              )
                            )
                          }
                          type="button"
                          onClick={() =>
                            selectStudent(
                              student,
                              'EXISTENTE',
                            )
                          }
                        >
                          <span className="student-avatar">
                            {student.nombres
                              .charAt(0)
                              .toUpperCase()}

                            {student.apellidos
                              .charAt(0)
                              .toUpperCase()}
                          </span>

                          <span className="enrollment-student-copy">
                            <strong>
                              {student.nombres}
                              {' '}
                              {student.apellidos}
                            </strong>

                            <small>
                              {
                                student
                                  .codigo_estudiante
                              }
                            </small>
                          </span>

                          {selected && (
                            <CheckCircle2
                              size={19}
                              aria-hidden="true"
                            />
                          )}
                        </button>
                      )
                    },
                  )}
                </div>
              )}
            </>
          )}

          {step === 2 &&
            selectedStudent && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 2
                  </span>

                  <h2>
                    Datos
                  </h2>

                  <p>
                    Los datos registrados del
                    estudiante se reutilizan
                    automáticamente. Solo
                    edítalos si hubo cambios.
                  </p>
                </div>
              </header>

              <div className="student-data-notice">
                <CheckCircle2
                  size={20}
                  aria-hidden="true"
                />

                <div>
                  <strong>
                    {studentOrigin ===
                    'EXISTENTE'
                      ? (
                        'Datos existentes ' +
                        'aplicados'
                      )
                      : (
                        'Datos del nuevo ' +
                        'estudiante aplicados'
                      )}
                  </strong>

                  <p>
                    No necesitas volver a
                    escribir la información
                    personal del estudiante.
                  </p>
                </div>
              </div>

              <div className="student-data-header">
                <div>
                  <span className="dashboard-card-eyebrow">
                    {
                      selectedStudent
                        .codigo_estudiante
                    }
                  </span>

                  <h3>
                    {selectedStudent.nombres}
                    {' '}
                    {selectedStudent.apellidos}
                  </h3>
                </div>

                <PermissionGate
                  anyOf={[
                    PERMISSIONS
                      .ESTUDIANTES_GESTIONAR,
                  ]}
                >
                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={
                      openEditStudent
                    }
                  >
                    <Pencil
                      size={15}
                      aria-hidden="true"
                    />

                    Editar datos
                  </button>
                </PermissionGate>
              </div>

              <div className="student-data-grid">
                <article>
                  <span>
                    CUI
                  </span>

                  <strong>
                    {displayValue(
                      selectedStudent.cui,
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    Fecha de nacimiento
                  </span>

                  <strong>
                    {displayDate(
                      selectedStudent
                        .fecha_nacimiento,
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    Teléfono
                  </span>

                  <strong>
                    {displayValue(
                      selectedStudent
                        .telefono,
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    WhatsApp
                  </span>

                  <strong>
                    {displayValue(
                      selectedStudent
                        .whatsapp,
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    Correo
                  </span>

                  <strong>
                    {displayValue(
                      selectedStudent
                        .email,
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    Estado
                  </span>

                  <strong>
                    {
                      selectedStudent
                        .estado
                    }
                  </strong>
                </article>

                <article className="student-data-full">
                  <span>
                    Dirección
                  </span>

                  <strong>
                    {displayValue(
                      selectedStudent
                        .direccion,
                    )}
                  </strong>
                </article>
              </div>

              <div className="enrollment-data-divider" />

              <div className="enrollment-form-grid">
                <label className="enrollment-field">
                  <span>
                    Tipo de inscripción
                  </span>

                  <select
                    value={tipo}
                    onChange={(event) =>
                      setTipo(
                        event.target
                          .value as
                          TipoInscripcion,
                      )
                    }
                  >
                    <option value="NUEVA">
                      Nueva inscripción
                    </option>

                    <option value="REINSCRIPCION">
                      Reinscripción
                    </option>

                    <option value="TRASLADO">
                      Traslado
                    </option>
                  </select>
                </label>

                <label className="enrollment-field enrollment-field-full">
                  <span>
                    Observaciones
                  </span>

                  <textarea
                    rows={4}
                    value={observaciones}
                    placeholder={
                      (
                        'Observaciones opcionales ' +
                        'de la inscripción'
                      )
                    }
                    onChange={(event) =>
                      setObservaciones(
                        event.target.value,
                      )
                    }
                  />
                </label>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 3
                  </span>

                  <h2>
                    Oferta académica
                  </h2>

                  <p>
                    Selecciona el ciclo,
                    la carrera y el grado
                    para esta inscripción.
                  </p>
                </div>
              </header>

              <div className="enrollment-form-grid">
                <label className="enrollment-field">
                  <span>
                    Ciclo escolar
                  </span>

                  <select
                    value={
                      selectedCicloId ??
                      ''
                    }
                    onChange={(event) =>
                      handleCicloChange(
                        event.target.value,
                      )
                    }
                  >
                    <option value="">
                      Selecciona un ciclo
                    </option>

                    {ciclos.map(
                      (ciclo) => (
                        <option
                          key={
                            ciclo.id_ciclo
                          }
                          value={
                            ciclo.id_ciclo
                          }
                        >
                          {ciclo.nombre}
                          {' — '}
                          {ciclo.estado}
                        </option>
                      ),
                    )}
                  </select>
                </label>

                <label className="enrollment-field">
                  <span>
                    Carrera
                  </span>

                  <select
                    value={
                      selectedCarreraCicloId ??
                      ''
                    }
                    disabled={
                      !selectedCicloId ||
                      carreraCiclosQuery
                        .isLoading
                    }
                    onChange={(event) =>
                      handleCarreraChange(
                        event.target.value,
                      )
                    }
                  >
                    <option value="">
                      Selecciona una carrera
                    </option>

                    {carreraCiclos.map(
                      (item) => {
                        const carrera =
                          carrerasPorId.get(
                            item.id_carrera,
                          )

                        return (
                          <option
                            key={
                              item.id_carrera_ciclo
                            }
                            value={
                              item.id_carrera_ciclo
                            }
                          >
                            {item
                              .nombre_comercial ||
                              carrera
                                ?.nombre ||
                              (
                                'Carrera #' +
                                item.id_carrera
                              )}
                          </option>
                        )
                      },
                    )}
                  </select>
                </label>

                <label className="enrollment-field enrollment-field-full">
                  <span>
                    Grado
                  </span>

                  <select
                    value={
                      selectedGradoId ??
                      ''
                    }
                    disabled={
                      !selectedCarreraCicloId ||
                      gradosQuery.isLoading
                    }
                    onChange={(event) =>
                      setSelectedGradoId(
                        event.target.value
                          ? Number(
                              event.target
                                .value,
                            )
                          : null,
                      )
                    }
                  >
                    <option value="">
                      Selecciona un grado
                    </option>

                    {grados.map(
                      (grado) => (
                        <option
                          key={
                            grado.id_grado
                          }
                          value={
                            grado.id_grado
                          }
                        >
                          {grado.nombre}
                        </option>
                      ),
                    )}
                  </select>
                </label>
              </div>

              {(ciclosQuery.isError ||
                carrerasQuery.isError ||
                carreraCiclosQuery
                  .isError ||
                gradosQuery.isError) && (
                <div className="form-error">
                  No fue posible cargar
                  completamente la oferta
                  académica.
                </div>
              )}
            </>
          )}

          {step === 4 &&
            selectedStudent && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 4
                  </span>

                  <h2>
                    Expediente
                  </h2>

                  <p>
                    Revisa documentos
                    entregados, pendientes
                    y archivos digitalizados.
                  </p>
                </div>
              </header>

              <ExpedienteChecklist
                idEstudiante={
                  selectedStudent
                    .id_estudiante
                }
                onSummaryChange={
                  setExpedienteSummary
                }
              />
            </>
          )}

          {step === 5 &&
            selectedStudent && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 5
                  </span>

                  <h2>
                    Encargado
                  </h2>

                  <p>
                    Consulta o registra madre,
                    padre, tutor u otros
                    contactos del estudiante.
                  </p>
                </div>
              </header>

              <ContactosStep
                idEstudiante={
                  selectedStudent
                    .id_estudiante
                }
                onContactsChange={
                  setContactos
                }
              />
            </>
          )}

          {step === 6 && (
            <>
              <header className="enrollment-section-header">
                <div>
                  <span>
                    Paso 6
                  </span>

                  <h2>
                    Confirmar inscripción
                  </h2>

                  <p>
                    Revisa la información
                    antes de registrar.
                  </p>
                </div>
              </header>

              <div className="enrollment-confirm-grid">
                <article>
                  <span>
                    Estudiante
                  </span>

                  <strong>
                    {selectedStudent
                      ? (
                        (
                          selectedStudent
                            .nombres +
                          ' ' +
                          selectedStudent
                            .apellidos
                        )
                      )
                      : '—'}
                  </strong>

                  <small>
                    {selectedStudent
                      ?.codigo_estudiante ??
                      ''}
                  </small>
                </article>

                <article>
                  <span>
                    Tipo
                  </span>

                  <strong>
                    {tipoLabels[tipo]}
                  </strong>

                  <small>
                    {studentOrigin ===
                    'EXISTENTE'
                      ? 'Estudiante existente'
                      : 'Nuevo estudiante'}
                  </small>
                </article>

                <article>
                  <span>
                    Ciclo
                  </span>

                  <strong>
                    {selectedCiclo
                      ?.nombre ??
                      '—'}
                  </strong>

                  <small>
                    {selectedCiclo
                      ?.estado ??
                      ''}
                  </small>
                </article>

                <article>
                  <span>
                    Carrera
                  </span>

                  <strong>
                    {selectedCarreraNombre ||
                      '—'}
                  </strong>
                </article>

                <article>
                  <span>
                    Grado
                  </span>

                  <strong>
                    {selectedGrado
                      ?.nombre ??
                      '—'}
                  </strong>
                </article>

                <article>
                  <span>
                    Expediente
                  </span>

                  <strong>
                    {expedienteSummary
                      ? (
                        (
                          expedienteSummary
                            .entregados +
                          ' de ' +
                          expedienteSummary
                            .requeridos +
                          ' requeridos'
                        )
                      )
                      : (
                        'Sin resumen ' +
                        'disponible'
                      )}
                  </strong>

                  {expedienteSummary && (
                    <small>
                      {
                        expedienteSummary
                          .pendientes
                      }
                      {' pendientes'}
                    </small>
                  )}
                </article>

                <article>
                  <span>
                    Contacto principal
                  </span>

                  <strong>
                    {contactoPrincipal
                      ?.nombre ??
                      'No definido'}
                  </strong>

                  <small>
                    {contactoPrincipal
                      ? (
                        contactoPrincipal
                          .parentesco ||
                        'Sin parentesco'
                      )
                      : (
                        contactos.length > 0
                          ? (
                            contactos.length +
                            ' contacto(s) registrado(s)'
                          )
                          : (
                            'Sin encargados registrados'
                          )
                      )}
                  </small>
                </article>

                {contactoPrincipal && (
                  <article>
                    <span>
                      Teléfono encargado
                    </span>

                    <strong>
                      {contactoPrincipal
                        .whatsapp ||
                        contactoPrincipal
                          .telefono ||
                        'No registrado'}
                    </strong>

                    <small>
                      {contactoPrincipal
                        .email ||
                        ''}
                    </small>
                  </article>
                )}
              </div>

              {observaciones.trim() && (
                <div className="enrollment-observations">
                  <span>
                    Observaciones
                  </span>

                  <p>
                    {observaciones}
                  </p>
                </div>
              )}

              {createInscripcionMutation
                .isError && (
                <div className="form-error">
                  {getApiErrorMessage(
                    createInscripcionMutation
                      .error,
                    (
                      'No fue posible registrar ' +
                      'la inscripción.'
                    ),
                  )}
                </div>
              )}
            </>
          )}
        </div>

        <footer className="enrollment-wizard-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={
              step === 1
                ? onClose
                : handlePrevious
            }
          >
            {step === 1 ? (
              'Cancelar'
            ) : (
              <>
                <ChevronLeft
                  size={16}
                  aria-hidden="true"
                />

                Anterior
              </>
            )}
          </button>

          {step < 6 ? (
            <button
              className="button button-primary"
              type="button"
              disabled={
                !canContinue()
              }
              onClick={
                handleNext
              }
            >
              Siguiente

              <ChevronRight
                size={16}
                aria-hidden="true"
              />
            </button>
          ) : (
            <button
              className="button button-primary"
              type="button"
              disabled={
                createInscripcionMutation
                  .isPending
              }
              onClick={() => {
                void handleSubmit()
              }}
            >
              {createInscripcionMutation
                .isPending
                ? 'Registrando...'
                : 'Registrar inscripción'}
            </button>
          )}
        </footer>
      </section>

      {showStudentForm && (
        <EstudianteFormModal
          title={
            editingStudent
              ? 'Editar estudiante'
              : 'Registrar estudiante'
          }
          estudiante={
            editingStudent
              ? selectedStudent ??
                undefined
              : undefined
          }
          isSubmitting={
            createStudentMutation
              .isPending ||
            updateStudentMutation
              .isPending
          }
          error={
            createStudentMutation
              .isError
              ? getApiErrorMessage(
                  createStudentMutation
                    .error,
                  (
                    'No fue posible registrar ' +
                    'el estudiante.'
                  ),
                )
              : updateStudentMutation
                  .isError
                ? getApiErrorMessage(
                    updateStudentMutation
                      .error,
                    (
                      'No fue posible actualizar ' +
                      'el estudiante.'
                    ),
                  )
                : null
          }
          onClose={
            closeStudentForm
          }
          onSubmit={
            handleStudentSubmit
          }
        />
      )}
    </>
  )
}


export default InscripcionWizard