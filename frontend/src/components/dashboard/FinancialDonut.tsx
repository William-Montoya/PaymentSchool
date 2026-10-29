import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

import {
  formatCurrency,
} from '../../utils/formatters'

interface FinancialDonutProps {
  totalPagado: string
  deudaTotal: string
}

function FinancialDonut({
  totalPagado,
  deudaTotal,
}: FinancialDonutProps) {
  const paid =
    Number(totalPagado) || 0

  const debt =
    Number(deudaTotal) || 0

  const total =
    paid + debt

  const percentage =
    total > 0
      ? Math.round(
          (paid / total) * 100,
        )
      : 0

  const data = [
    {
      name: 'Pagado',
      value: paid,
    },
    {
      name: 'Deuda',
      value: debt,
    },
  ]

  return (
    <article className="dashboard-card donut-card">
      <header className="dashboard-card-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Finanzas
          </span>

          <h2>
            Distribución financiera
          </h2>
        </div>
      </header>

      <div className="donut-content">
        <div className="donut-chart">
          <ResponsiveContainer
            width="100%"
            height={230}
          >
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={68}
                outerRadius={94}
                paddingAngle={3}
                stroke="none"
              >
                <Cell
                  fill="#7c4dff"
                />

                <Cell
                  fill="#242444"
                />
              </Pie>

              <Tooltip
                formatter={(
                  value,
                ) =>
                  formatCurrency(
                    Number(value),
                  )
                }
              />
            </PieChart>
          </ResponsiveContainer>

          <div className="donut-center">
            <strong>
              {percentage}%
            </strong>

            <span>
              cubierto
            </span>
          </div>
        </div>

        <div className="donut-legend">
          <div>
            <span
              className={
                'legend-dot ' +
                'legend-purple'
              }
            />

            <div>
              <small>
                Pagado
              </small>

              <strong>
                {formatCurrency(
                  paid,
                )}
              </strong>
            </div>
          </div>

          <div>
            <span
              className={
                'legend-dot ' +
                'legend-navy'
              }
            />

            <div>
              <small>
                Deuda
              </small>

              <strong>
                {formatCurrency(
                  debt,
                )}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}

export default FinancialDonut