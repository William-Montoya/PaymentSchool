import type {
  LucideIcon,
} from 'lucide-react'

interface KpiCardProps {
  label: string
  value: string
  helper: string
  icon: LucideIcon
  tone?:
    | 'purple'
    | 'orange'
    | 'coral'
    | 'navy'
    | 'green'
}

function KpiCard({
  label,
  value,
  helper,
  icon: Icon,
  tone = 'purple',
}: KpiCardProps) {
  return (
    <article className="kpi-card">
      <div
        className={
          `kpi-icon kpi-${tone}`
        }
      >
        <Icon
          size={20}
          strokeWidth={1.9}
          aria-hidden="true"
        />
      </div>

      <div className="kpi-content">
        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {helper}
        </small>
      </div>
    </article>
  )
}

export default KpiCard