export interface PulseSuggestion {
  id: string
  priority: 'HAUTE' | 'MOYENNE' | 'BASSE'
  category: string
  title: string
  explainability: string
  cta: string
  status: 'active' | 'activated'
}

export function usePulseDemo() {
  const customer = useState('pulse-customer', () => ({
    name: 'Marc Dupont',
    age: 28,
    profile: 'Jeune Actif - Profil Investisseur Dynamique',
    totalCapital: 45000,
    investments: { total: 12400, trend30d: '+4.2%' },
    payments: [
      { label: 'Loyer Résidence', amount: 950, date: '01 Oct 2026' },
      { label: 'Assurance Habitation KBC', amount: 42, date: '05 Oct 2026' },
      { label: 'Échéance Épargne Auto', amount: 200, date: '10 Oct 2026' },
    ],
  }))

  const suggestions = useState<PulseSuggestion[]>('pulse-suggestions', () => [
    {
      id: 'sug-01', priority: 'HAUTE', category: 'Assurance',
      title: 'Achat de véhicule détecté — Assurance Auto',
      explainability: "Détecté via transaction « BMW Garage Brussels » (18 500 €). Aucun contrat auto actif trouvé dans votre portefeuille KBC Insurance.",
      cta: "Voir l'offre Auto", status: 'active',
    },
    {
      id: 'sug-02', priority: 'HAUTE', category: 'Prêt',
      title: "Capacité d'emprunt élevée — Projet Immobilier",
      explainability: 'Capital disponible supérieur à 40 000 € et revenus réguliers. Profil éligible au Prêt Hypothécaire KBC Taux Jeune.',
      cta: 'Simuler mon prêt', status: 'active',
    },
    {
      id: 'sug-03', priority: 'MOYENNE', category: 'Investissement',
      title: "Optimisation de l'excédent de trésorerie",
      explainability: '3 000 € disponibles sur le compte courant. Proposition de placement sur Fonds d’Investissement KBC Life.',
      cta: 'Placer en 1-click', status: 'active',
    },
  ])

  const toastMessage = useState('pulse-toast', () => '')
  const activeSuggestionCount = computed(() => suggestions.value.filter((item) => item.status === 'active').length)

  function notify(message: string) {
    toastMessage.value = message
    if (import.meta.client) {
      window.setTimeout(() => {
        if (toastMessage.value === message) toastMessage.value = ''
      }, 2800)
    }
  }

  function activateSuggestion(id: string) {
    const item = suggestions.value.find((suggestion) => suggestion.id === id)
    if (!item) return
    item.status = 'activated'
    notify('Votre demande est prête. Un conseiller KBC vous accompagnera. (Démo)')
  }

  function dismissSuggestion(id: string) {
    suggestions.value = suggestions.value.filter((suggestion) => suggestion.id !== id)
    notify('Suggestion ignorée')
  }

  return { customer, suggestions, activeSuggestionCount, toastMessage, notify, activateSuggestion, dismissSuggestion }
}