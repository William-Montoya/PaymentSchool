import {
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

import {
  useMemo,
  useState,
} from 'react'

import type {
  EvaluacionDetalle,
} from '../../types/evaluacion'

interface DashboardCalendarProps {
  evaluations: EvaluacionDetalle[]
  canViewAcademic: boolean
}

interface CalendarEvent {
  id: string
  date: string
  title: string
  type:
    | 'evaluation'
    | 'cutoff'
}

const DAYS = [
  'Lun',
  'Mar',
  'Mié',
  'Jue',
  'Vie',
  'Sáb',
  'Dom',
]

function dateKey(
  year: number,
  month: number,
  day: number,
) {
  const mm =
    String(
      month + 1,
    ).padStart(
      2,
      '0',
    )

  const dd =
    String(day).padStart(
      2,
      '0',
    )

  return `${year}-${mm}-${dd}`
}

function DashboardCalendar({
  evaluations,
  canViewAcademic,
}: DashboardCalendarProps) {
  const today = new Date()

  const [
    currentMonth,
    setCurrentMonth,
  ] = useState(
    () =>
      new Date(
        today.getFullYear(),
        today.getMonth(),
        1,
      ),
  )

  const events =
    useMemo<CalendarEvent[]>(
      () =>
        evaluations.flatMap(
          (evaluation) => [
            {
              id:
                `evaluation-${evaluation.id_evaluacion}`,
              date:
                evaluation.fecha_evaluacion,
              title:
                evaluation.nombre,
              type:
                'evaluation',
            },
            {
              id:
                `cutoff-${evaluation.id_evaluacion}`,
              date:
                evaluation.fecha_corte_finanzas,
              title:
                `Corte: ${evaluation.nombre}`,
              type:
                'cutoff',
            },
          ],
        ),
      [evaluations],
    )

  const year =
    currentMonth.getFullYear()

  const month =
    currentMonth.getMonth()

  const monthLabel =
    new Intl.DateTimeFormat(
      'es-GT',
      {
        month: 'long',
        year: 'numeric',
      },
    ).format(
      currentMonth,
    )

  const firstDay =
    new Date(
      year,
      month,
      1,
    )

  const daysInMonth =
    new Date(
      year,
      month + 1,
      0,
    ).getDate()

  const mondayBasedOffset =
    (
      firstDay.getDay() +
      6
    ) % 7

  const cells:
    Array<number | null> = [
      ...Array.from(
        {
          length:
            mondayBasedOffset,
        },
        () => null,
      ),

      ...Array.from(
        {
          length:
            daysInMonth,
        },
        (_, index) =>
          index + 1,
      ),
    ]

  while (
    cells.length % 7 !== 0
  ) {
    cells.push(null)
  }

  const selectedMonthEvents =
    events
      .filter((event) =>
        event.date.startsWith(
          `${year}-${String(
            month + 1,
          ).padStart(
            2,
            '0',
          )}`,
        ),
      )
      .sort((a, b) =>
        a.date.localeCompare(
          b.date,
        ),
      )

  function previousMonth() {
    setCurrentMonth(
      (current) =>
        new Date(
          current.getFullYear(),
          current.getMonth() - 1,
          1,
        ),
    )
  }

  function nextMonth() {
    setCurrentMonth(
      (current) =>
        new Date(
          current.getFullYear(),
          current.getMonth() + 1,
          1,
        ),
    )
  }

  return (
    <article className="dashboard-card calendar-card">
      <header className="calendar-header">
        <div>
          <span className="dashboard-card-eyebrow">
            Agenda
          </span>

          <h2>
            Calendario
          </h2>
        </div>

        <div className="calendar-navigation">
          <button
            type="button"
            onClick={previousMonth}
            aria-label="Mes anterior"
          >
            <ChevronLeft
              size={17}
              aria-hidden="true"
            />
          </button>

          <strong>
            {monthLabel}
          </strong>

          <button
            type="button"
            onClick={nextMonth}
            aria-label="Mes siguiente"
          >
            <ChevronRight
              size={17}
              aria-hidden="true"
            />
          </button>
        </div>
      </header>

      <div className="calendar-weekdays">
        {DAYS.map((day) => (
          <span key={day}>
            {day}
          </span>
        ))}
      </div>

      <div className="calendar-grid">
        {cells.map(
          (
            day,
            index,
          ) => {
            if (day === null) {
              return (
                <span
                  className="calendar-day calendar-day-empty"
                  key={`empty-${index}`}
                />
              )
            }

            const key =
              dateKey(
                year,
                month,
                day,
              )

            const dayEvents =
              events.filter(
                (event) =>
                  event.date === key,
              )

            const isToday =
              year ===
                today.getFullYear() &&
              month ===
                today.getMonth() &&
              day ===
                today.getDate()

            return (
              <div
                className={[
                  'calendar-day',
                  isToday
                    ? 'calendar-day-today'
                    : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                key={key}
              >
                <span>
                  {day}
                </span>

                {dayEvents.length >
                  0 && (
                  <div className="calendar-markers">
                    {dayEvents
                      .slice(
                        0,
                        2,
                      )
                      .map(
                        (event) => (
                          <i
                            className={
                              event.type ===
                              'evaluation'
                                ? (
                                  'calendar-marker ' +
                                  'marker-purple'
                                )
                                : (
                                  'calendar-marker ' +
                                  'marker-orange'
                                )
                            }
                            key={event.id}
                            title={
                              event.title
                            }
                          />
                        ),
                      )}
                  </div>
                )}
              </div>
            )
          },
        )}
      </div>

      <div className="calendar-events">
        {!canViewAcademic ? (
          <p className="calendar-empty">
            Los eventos académicos requieren
            permiso de consulta académica.
          </p>
        ) : selectedMonthEvents.length >
          0 ? (
          selectedMonthEvents
            .slice(
              0,
              4,
            )
            .map(
              (event) => (
                <div
                  className="calendar-event"
                  key={event.id}
                >
                  <span
                    className={
                      event.type ===
                      'evaluation'
                        ? (
                          'event-indicator ' +
                          'event-purple'
                        )
                        : (
                          'event-indicator ' +
                          'event-orange'
                        )
                    }
                  />

                  <div>
                    <strong>
                      {event.title}
                    </strong>

                    <small>
                      {new Intl.DateTimeFormat(
                        'es-GT',
                        {
                          day: '2-digit',
                          month: 'short',
                        },
                      ).format(
                        new Date(
                          `${event.date}T00:00:00`,
                        ),
                      )}
                    </small>
                  </div>
                </div>
              ),
            )
        ) : (
          <p className="calendar-empty">
            No hay evaluaciones ni cortes
            registrados para este mes.
          </p>
        )}
      </div>
    </article>
  )
}

export default DashboardCalendar