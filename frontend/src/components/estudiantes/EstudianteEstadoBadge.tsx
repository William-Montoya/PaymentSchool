import type {
  EstadoEstudiante,
} from '../../types/estudiante'

interface Props {
  estado: EstadoEstudiante
}

function EstudianteEstadoBadge({
  estado,
}: Props) {
  const className =
    `student-status student-status-${estado.toLowerCase()}`

  return (
    <span className={className}>
      {estado}
    </span>
  )
}

export default EstudianteEstadoBadge