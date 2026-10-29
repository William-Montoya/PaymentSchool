import {
  Bell,
  BookOpenCheck,
  ChartNoAxesCombined,
  ClipboardList,
  FileClock,
  FolderOpen,
  GraduationCap,
  LayoutDashboard,
  ShieldCheck,
  WalletCards,
  type LucideIcon,
} from 'lucide-react'

import {
  PERMISSIONS,
  type PermissionName,
} from '../auth/permissions'

export interface NavigationItem {
  label: string
  path: string
  icon: LucideIcon
  permissions?: readonly PermissionName[]
}

export interface NavigationSection {
  label: string
  items: readonly NavigationItem[]
}

export const navigationSections:
  readonly NavigationSection[] = [
    {
      label: 'Principal',
      items: [
        {
          label: 'Inicio',
          path: '/',
          icon: LayoutDashboard,
        },
      ],
    },

    {
      label: 'Gestión académica',
      items: [
        {
          label: 'Estudiantes',
          path: '/estudiantes',
          icon: GraduationCap,
          permissions: [
            PERMISSIONS.ESTUDIANTES_VER,
          ],
        },

        {
          label: 'Inscripciones',
          path: '/inscripciones',
          icon: ClipboardList,
          permissions: [
            PERMISSIONS.ACADEMICO_VER,
          ],
        },

        {
          label: 'Expedientes',
          path: '/expedientes',
          icon: FolderOpen,
          permissions: [
            PERMISSIONS.EXPEDIENTES_VER,
          ],
        },

        {
          label: 'Configuración académica',
          path: '/academico',
          icon: BookOpenCheck,
          permissions: [
            PERMISSIONS.ACADEMICO_VER,
          ],
        },
      ],
    },

    {
      label: 'Finanzas',
      items: [
        {
          label: 'Gestión financiera',
          path: '/finanzas',
          icon: WalletCards,
          permissions: [
            PERMISSIONS.FINANZAS_VER,
          ],
        },

        {
          label: 'Pagos',
          path: '/pagos',
          icon: ClipboardList,
          permissions: [
            PERMISSIONS.FINANZAS_VER,
          ],
        },

        {
          label: 'Reportes',
          path: '/reportes',
          icon: ChartNoAxesCombined,
          permissions: [
            PERMISSIONS.REPORTES_VER,
          ],
        },
      ],
    },

    {
      label: 'Comunicación',
      items: [
        {
          label: 'Notificaciones',
          path: '/notificaciones',
          icon: Bell,
          permissions: [
            PERMISSIONS.NOTIFICACIONES_VER,
          ],
        },
      ],
    },

    {
      label: 'Administración',
      items: [
        {
          label: 'Seguridad',
          path: '/seguridad',
          icon: ShieldCheck,
          permissions: [
            PERMISSIONS.SEGURIDAD_VER,
          ],
        },

        {
          label: 'Auditoría',
          path: '/auditoria',
          icon: FileClock,
          permissions: [
            PERMISSIONS.AUDITORIA_VER,
          ],
        },
      ],
    },
  ]
