export interface Contacto {
  id_contacto: number
  id_estudiante: number

  nombre: string
  parentesco: string | null

  telefono: string | null
  whatsapp: string | null
  email: string | null

  es_principal: boolean
  activo: boolean
}


export interface ContactoCreate {
  id_estudiante: number

  nombre: string
  parentesco?: string | null

  telefono?: string | null
  whatsapp?: string | null
  email?: string | null

  es_principal?: boolean
}


export interface ContactoUpdate {
  nombre?: string | null
  parentesco?: string | null

  telefono?: string | null
  whatsapp?: string | null
  email?: string | null

  es_principal?: boolean | null
}