import type { DistrictRow, ProfileType, TypologyDefinition } from '../api/types'
import { Badge } from './Badge'

const ORDER: ProfileType[] = ['compound_gap', 'access_gap', 'poverty_led', 'lower_relative_need']

type Props = {
  districts: DistrictRow[]
  typology: Record<ProfileType, TypologyDefinition>
  selected: string | null
  onSelect: (district: string) => void
}

export function ProfileSummary({ districts, typology, selected, onSelect }: Props) {
  return (
    <aside className="context-card profile-summary" aria-labelledby="profiles-title">
      <h3 id="profiles-title">
        District profiles <Badge kind="estimate" />
      </h3>
      {ORDER.map((type) => {
        const members = districts.filter((d) => d.profile.type === type)
        return (
          <section key={type} className="profile-group">
            <p className={`profile-chip profile-${type}`}>
              {typology[type].label} <span className="count">{members.length}</span>
            </p>
            <p className="small muted">{typology[type].rule}.</p>
            <ul className="chip-list">
              {members.map((d) => (
                <li key={d.district}>
                  <button
                    type="button"
                    className="chip"
                    aria-pressed={d.district === selected}
                    onClick={() => onSelect(d.district)}
                  >
                    {d.district}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )
      })}
    </aside>
  )
}
