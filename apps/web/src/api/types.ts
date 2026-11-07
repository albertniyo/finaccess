/** Response shapes of the FastAPI backend (see backend/compass). */

export type Kind = 'observed' | 'estimate' | 'scenario' | 'recommendation'

export type Measure = 'excluded' | 'not_formally_served'

export type Estimate = {
  value: number
  se?: number
  ci?: [number, number]
  cv?: number
  uncertainty: 'published' | 'approximate' | 'modelled'
  poverty_2017_modelled?: number
}

export type ProfileType = 'compound_gap' | 'poverty_led' | 'access_gap' | 'lower_relative_need'

export type Profile = {
  type: ProfileType
  label: string
  confidence: { poverty_vs_national: string; exclusion_vs_national: string }
  flags: { id: string; label: string; detail: string; source: string }[]
}

export type AccessStrand = {
  banked: number
  other_formal: number
  informal_only: number
  excluded: number
}

export type IndicatorId =
  | 'poverty_rate'
  | 'excluded'
  | 'not_formally_served'
  | 'informal_only'
  | 'banked'
  | 'poverty_decrease'
  | 'mobile_phone_households'
  | 'smartphone_households'
  | 'internet_households'
  | 'health_insurance'

export type IndicatorMeta = {
  id: IndicatorId
  label: string
  unit: string
  definition: string
  survey: string
  source: string
  reference: string
  geo_levels: string[]
  higher_is_worse: boolean
  kind: Kind
  uncertainty: string
  group: 'core' | 'context'
}

type AreaValues = Record<IndicatorId, Estimate> & {
  access_strand: AccessStrand
  transcription_note: string | null
}

export type DistrictRow = AreaValues & {
  district: string
  province: string
  profile: Profile
}

export type ProvinceRow = AreaValues & { province: string; extreme_poverty_rate: Estimate }

export type NationalRow = AreaValues & {
  extreme_poverty_rate: Estimate
  urban_poverty_rate: Estimate
  rural_poverty_rate: Estimate
  poverty_2017_modelled: number
}

export type TypologyDefinition = { label: string; rule: string; response_focus: string }

export type GroupStrand = {
  dimension: string
  dimension_label: string
  group: string
  access_strand: AccessStrand
  excluded: number
  formally_served: number
  source_figure: string
  transcription_note: string | null
}

export type WhoIsExcluded = {
  groups: GroupStrand[]
  national_trend: { year: number; access_strand: AccessStrand }[]
  products: { product: string; percent_adults: number; source: string; note: string | null }[]
  vup: {
    beneficiaries_thousands: number
    population_thousands: number
    poverty_rate_beneficiaries: number
    poverty_rate_all: number
    component_shares: Record<string, number>
    reference: string
  }
  highlights: string[]
  provenance: { kind: Kind; geo_level: string; references: Record<string, string>; note: string }
}

export type IndicatorsResponse = {
  status: string
  geo_level: string
  filters: { province: string | null; available: { province: string[] } }
  unsupported_filters: Record<string, string>
  indicators: IndicatorMeta[]
  national: NationalRow
  provinces: ProvinceRow[]
  districts: DistrictRow[]
  who_is_excluded: WhoIsExcluded
  typology: Record<ProfileType, TypologyDefinition>
  flags: Record<string, { label: string; rule: string }>
  provenance: {
    kind: Kind
    references: Record<string, string>
    uncertainty_assumptions: { note: string }
    known_discrepancies: { item: string; detail: string }[]
    linkage: string
  }
}

export type Mover = {
  district: string
  rank: number
  baseline_rank: number
  poverty_rate: number
  exclusion: number
  exclusion_rank: number
  explanation: string
}

export type Ranking = {
  district: string
  province: string
  rank: number
  baseline_rank: number
  exclusion_rank: number
  rank_shift: number
  score: number
  inputs: { poverty_rate: number; exclusion: number }
  normalised: { poverty: number; exclusion: number }
  contributions: { poverty: number; exclusion: number }
  uncertainty: { p_top5: number; p_top10: number; rank_interval_90: [number, number] }
  top5_poverty_weight_range: [number, number] | null
  profile: Profile
}

export type SensitivityScheme = {
  poverty_weight: number
  label: string
  measure: Measure
  top5: string[]
  top10: string[]
}

export type PrioritiesResponse = {
  status: string
  weights: { poverty: number; exclusion: number; note: string }
  measure: { id: Measure; label: string }
  measures: Record<Measure, string>
  national: { poverty_rate: number; exclusion: number }
  rankings: Ranking[]
  comparison: Record<
    'top5' | 'top10',
    { baseline: string[]; combined: string[]; overlap: string[]; entered: Mover[]; dropped: Mover[] }
  >
  sensitivity: { schemes: SensitivityScheme[]; robust_top5: string[] }
  provenance: {
    kind: Kind
    formula: string
    normalisation: string
    uncertainty: { method: string; poverty: string; exclusion: string }
    limitations: string[]
  }
}

export type Strategy = 'poverty_only' | 'exclusion_gap' | 'combined_score'
export type AllocationRule = 'equal' | 'proportional'

export type ScenarioRequest = {
  budget: number
  strategy: Strategy
  topN: number
  allocation: AllocationRule
  povertyWeight: number
  exclusionWeight: number
  measure: Measure
}

export type ScenarioResponse = {
  status: string
  label: 'scenario'
  budget: number
  strategy: Strategy
  strategy_label: string
  top_n: number
  allocation: AllocationRule
  allocation_label: string
  allocations: {
    district: string
    province: string
    share: number
    amount: number
    poverty_rate: number
    exclusion: number
    profile: string
  }[]
  comparison: {
    strategy: Strategy
    label: string
    districts: string[]
    budget_share_above_national_poverty: number
    budget_share_above_national_exclusion: number
    budget_share_access_gap_districts: number
    overlap_with_selected: number
    only_in_this_strategy: string[]
  }[]
  strategies: Record<Strategy, string>
  allocation_rules: Record<AllocationRule, string>
  provenance: { kind: 'scenario'; warning: string; assumptions: string[] }
}

export type Statement = { text: string; kind: Kind; source: string | null }

export type Source = {
  id: string
  title: string
  publisher: string
  year: string
  role: string
  geo_level: string
  url: string
  landing_page?: string
  catalogue?: string
  transcription?: string
  sha256?: string
  retrieved_at?: string | null
}

export type BriefResponse = {
  status: string
  geo: string
  province: string
  generated_on: string
  title: string
  weights: { poverty: number; exclusion: number }
  measure: { id: Measure; label: string }
  summary: {
    poverty_rate: number
    excluded: number
    rank: number
    baseline_rank: number
    rank_shift: number
    profile: Profile
    p_top5: number
    contributions: { poverty: number; exclusion: number }
  }
  sections: {
    key_findings: Statement[]
    interpretation: Statement[]
    next_steps: Statement[]
    scenario: Statement[]
    methodology_notes: string[]
    limitations: string[]
    sources: Source[]
  }
}

export type SourcesResponse = { sources: Source[]; note: string; linkage_policy: string }

export type ValidationResponse = {
  status: string
  passed: number
  failed: number
  checks: {
    check: string
    group: 'golden' | 'consistency' | 'transcription'
    expected: unknown
    observed: unknown
    tolerance: number
    pass: boolean
    reference: string
  }[]
  known_discrepancies: { item: string; detail: string }[]
}

export type MethodResponse = {
  indicators: IndicatorMeta[]
  measures: Record<Measure, { label: string }>
  formula: string
  schemes: { poverty_weight: number; label: string }[]
  uncertainty: {
    finscope_district_n: number
    finscope_assumed_deff: number
    rounding_variance_pp2: number
    note: string
  }
  simulations: number
  typology: Record<ProfileType, TypologyDefinition>
  limitations: string[]
  known_discrepancies: { item: string; detail: string }[]
}

export type GeoFeature = {
  type: 'Feature'
  properties: { district: string; province: string }
  geometry:
    | { type: 'Polygon'; coordinates: number[][][] }
    | { type: 'MultiPolygon'; coordinates: number[][][][] }
}

export type GeoCollection = { type: 'FeatureCollection'; features: GeoFeature[] }
