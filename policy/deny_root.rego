package main

import rego.v1

# Regle 1 : refuser les conteneurs qui s'executent en tant que root (runAsUser: 0)
deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	container.securityContext.runAsUser == 0
	msg := sprintf(
		"SECURITE : le conteneur '%s' s'execute en tant que root (runAsUser: 0). Utiliser un UID non-root.",
		[container.name],
	)
}

# Regle 2 : refuser quand runAsNonRoot est explicitement false
deny contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	container.securityContext.runAsNonRoot == false
	msg := sprintf(
		"SECURITE : le conteneur '%s' a runAsNonRoot: false. Definir runAsNonRoot: true.",
		[container.name],
	)
}

# Regle 3 : avertir quand aucun securityContext n'est defini
warn contains msg if {
	input.kind == "Deployment"
	some container in input.spec.template.spec.containers
	not container.securityContext
	msg := sprintf(
		"ATTENTION : le conteneur '%s' n'a pas de securityContext. Ajouter runAsNonRoot: true.",
		[container.name],
	)
}
