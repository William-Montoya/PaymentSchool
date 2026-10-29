const currencyFormatter =
  new Intl.NumberFormat(
    'es-GT',
    {
      style: 'currency',
      currency: 'GTQ',
      minimumFractionDigits: 2,
    },
  )

const integerFormatter =
  new Intl.NumberFormat(
    'es-GT',
    {
      maximumFractionDigits: 0,
    },
  )

export function formatCurrency(
  value: string | number,
): string {
  const numericValue =
    Number(value)

  if (
    !Number.isFinite(
      numericValue,
    )
  ) {
    return 'Q 0.00'
  }

  return currencyFormatter.format(
    numericValue,
  )
}

export function formatInteger(
  value: number,
): string {
  return integerFormatter.format(
    value,
  )
}