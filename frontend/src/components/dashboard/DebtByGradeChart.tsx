import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type {
  DeudaPorGrado,
} from '../../types/reportes'

import {
  formatCurrency,
} from '../../utils/formatters'

interface DebtByGradeChartProps {
  data: DeudaPorGrado[]
}

function DebtByGradeChart({
  data,
}: DebtByGradeChartProps) {
  const chartData =
    data.map((item) => ({
      grado: item.grado,
      estudiantes:
        item.cantidad_estudiantes,
      deuda:
        Number(
          item.deuda_total,
        ) || 0,
    }))

  return (
    <article className="dashboard-card debt-chart-card">
      <header className="dashboard-card-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Cartera
          </span>

          <h2>
            Deuda por grado
          </h2>

          <p>
            Saldo pendiente agrupado
            por grado.
          </p>
        </div>
      </header>

      {chartData.length > 0 ? (
        <div className="chart-container">
          <ResponsiveContainer
            width="100%"
            height={310}
          >
            <BarChart
              data={chartData}
              margin={{
                top: 10,
                right: 10,
                bottom: 5,
                left: 0,
              }}
            >
              <CartesianGrid
                stroke="#eceef4"
                vertical={false}
              />

              <XAxis
                dataKey="grado"
                tickLine={false}
                axisLine={false}
                tick={{
                  fill: '#8a91a5',
                  fontSize: 11,
                }}
              />

              <YAxis
                tickLine={false}
                axisLine={false}
                width={74}
                tick={{
                  fill: '#8a91a5',
                  fontSize: 11,
                }}
                tickFormatter={(
                  value,
                ) =>
                  `Q${Math.round(
                    Number(value) /
                      1000,
                  )}k`
                }
              />

              <Tooltip
                cursor={{
                  fill:
                    'rgba(124,77,255,0.05)',
                }}
                formatter={(
                  value,
                ) => [
                  formatCurrency(
                    Number(value),
                  ),
                  'Deuda',
                ]}
              />

              <Bar
                dataKey="deuda"
                fill="#7c4dff"
                radius={[
                  7,
                  7,
                  2,
                  2,
                ]}
                maxBarSize={44}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="dashboard-empty">
          No existen saldos por grado
          para mostrar.
        </div>
      )}
    </article>
  )
}

export default DebtByGradeChart