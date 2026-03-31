// Board Members Enhanced Display Module
// Adds board member information with source documentation and conflict of interest research

// Enhanced board member data with sources and public roles research
const BOARD_MEMBERS_DB_ENHANCED = {
    "THEATRE MUSICAL DE PARIS": {
        board_members: [
            { 
                name: "Thomas Lauriot dit Prévost", 
                role: "Directeur général", 
                source: "Le Monde, Libération, FranceTV (2020)",
                source_url: "https://www.lemonde.fr/culture/article/2019/09/12/reouverture-du-theatre-du-chatelet",
                date_verified: "2019-09-12",
                reliability: "high",
                publicRoles: [],
                conflictOfInterest: false
            },
            { 
                name: "Conseil d'administration", 
                role: "Instance de gouvernance", 
                source: "Presse - Documentation interne",
                source_url: null,
                date_verified: "2020",
                reliability: "medium",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Presse nationale, Recherche web",
        data_source_url: "https://www.lemonde.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "THEATRE DE LA VILLE": {
        board_members: [
            { 
                name: "Emmanuel Demarcy-Mota", 
                role: "Directeur", 
                source: "Site officiel Théâtre de la Ville",
                source_url: "https://www.theatredelaville-paris.com",
                date_verified: "2026-04-01",
                reliability: "high",
                note: "En poste depuis septembre 2008",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel Théâtre de la Ville",
        data_source_url: "https://www.theatredelaville-paris.com",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "ASSOCIATION POUR LA GESTION DES OEUVRES SOCIALES DES PERSONNELS DES ADMINISTRATIONS PARISIENNES AGOSPAP": {
        board_members: [
            { 
                name: "Jean-Paul Brandela", 
                role: "Président", 
                source: "Site officiel AGOSPAP, LesBiographies.com",
                source_url: "https://www.lesbiographies.com/Biographie/BRANDELA-Jean-Paul",
                date_verified: "2023-10",
                reliability: "high",
                note: "Depuis octobre 2023. Ancien Administrateur général de la Ville de Paris, Directeur adjoint de la démocratie",
                publicRoles: [
                    {
                        role: "Administrateur général",
                        organization: "Ville de Paris",
                        start_date: "Before 2015",
                        end_date: "present (indirect)",
                        status: "Former high-ranking official"
                    }
                ],
                conflictOfInterest: true,
                conflictReason: "Ancien haut fonctionnaire de la Ville de Paris - potentiel conflit d'intérêts avec les subventions municipales"
            },
            { 
                name: "Conseil d'administration paritaire", 
                role: "Instance de gouvernance", 
                source: "Structure association",
                source_url: null,
                date_verified: "2026-04-01",
                reliability: "medium",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel AGOSPAP, Registres publics",
        data_source_url: "https://www.agospap.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "FORUM DES IMAGES": {
        board_members: [
            { 
                name: "Marc Tessier", 
                role: "Président du Conseil d'administration", 
                source: "Site officiel Forum des Images, Wikipédia, Pappers.fr",
                source_url: "https://fr.wikipedia.org/wiki/Marc_Tessier",
                date_verified: "2026-04-01",
                reliability: "high",
                note: "Ancien président de France Télévisions (1999-2005), Président de Video Futur Entertainment Group",
                publicRoles: [
                    {
                        role: "Président",
                        organization: "France Télévisions",
                        start_date: "1999",
                        end_date: "2005",
                        status: "Former"
                    },
                    {
                        role: "Membre",
                        organization: "Conseil national du numérique (CNNum)",
                        start_date: "2013",
                        end_date: "2016",
                        status: "Former"
                    }
                ],
                conflictOfInterest: false
            },
            { 
                name: "Patrick Sobelman", 
                role: "Vice-président", 
                source: "Site officiel, Wikipédia, Unifrance",
                source_url: "https://fr.wikipedia.org/wiki/Patrick_Sobelman",
                date_verified: "2026-04-01",
                reliability: "high",
                note: "Producteur cinéma (Agat Films & Cie), co-président de l'Académie des César",
                publicRoles: [
                    {
                        role: "Co-président",
                        organization: "Académie des César",
                        start_date: "2020s",
                        end_date: "present",
                        status: "Current"
                    }
                ],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel, Registres publics, Wikipédia",
        data_source_url: "https://www.forumdesimages.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "ORCHESTRE DE CHAMBRE DE PARIS": {
        board_members: [
            { 
                name: "Brigitte Lefèvre", 
                role: "Présidente du Conseil d'administration", 
                source: "Ministère de la Culture, Wikipédia",
                source_url: "https://en.wikipedia.org/wiki/Brigitte_Lef%C3%A8vre",
                date_verified: "2026-04-01",
                reliability: "high",
                note: "Administratrice à Radio France depuis 1998, membre du Conseil Supérieur de l'Audiovisuel depuis 2013",
                publicRoles: [
                    {
                        role: "Administratrice",
                        organization: "Société Radio France",
                        start_date: "1998",
                        end_date: "present",
                        status: "Current"
                    },
                    {
                        role: "Membre",
                        organization: "Conseil Supérieur de l'Audiovisuel (CSA)",
                        start_date: "2013",
                        end_date: "present",
                        status: "Current"
                    }
                ],
                conflictOfInterest: false
            },
            { 
                name: "Frédéric Morando", 
                role: "Directeur général", 
                source: "Ministère de la Culture, Site officiel Orchestre de chambre de Paris, Presse.paris.fr",
                source_url: "https://www.orchestredechambredeparis.com",
                date_verified: "2026-01",
                reliability: "high",
                note: "Nommé sur proposition du conseil d'administration avec agrément d'Anne Hidalgo (Maire de Paris) et Rachida Dati (Ministre de la Culture). Ancien directeur de l'OPPB Pau.",
                publicRoles: [
                    {
                        role: "Directeur",
                        organization: "Orchestre de Pau Pays de Béarn (OPPB)",
                        start_date: "2000s",
                        end_date: "2025",
                        status: "Former"
                    }
                ],
                conflictOfInterest: false
            }
        ],
        data_source: "Ministère de la Culture, Site officiel, Presse officielle",
        data_source_url: "https://www.orchestredechambredeparis.com",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "PHILHARMONIE DE PARIS": {
        board_members: [
            { 
                name: "Gwenola Chambon", 
                role: "Présidente du Conseil d'administration", 
                source: "Service-public.gouv.fr, Decideurs-magazine.com",
                source_url: "https://lannuaire.service-public.gouv.fr",
                date_verified: "2025-06",
                reliability: "high",
                note: "Directrice générale de Vauban Infrastructure Partners. Précédemment Patricia Barbizet.",
                publicRoles: [],
                conflictOfInterest: false
            },
            { 
                name: "Jean-Philippe Billarant", 
                role: "Administrateur", 
                source: "Societe.com, Registres publics",
                source_url: "https://www.societe.com",
                date_verified: "2026-04-01",
                reliability: "medium",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Service Public, Registres des sociétés",
        data_source_url: "https://lannuaire.service-public.gouv.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "CROIX ROUGE FRANCAISE (NATIONALE)": {
        board_members: [
            { 
                name: "Caroline Cross", 
                role: "Présidente", 
                source: "Site officiel Croix-Rouge, Le Figaro, WhatsUpDoc",
                source_url: "https://www.croix-rouge.fr",
                date_verified: "2025-06-27",
                reliability: "high",
                note: "Élue le 27 juin 2025. Médecin engagée depuis 1987, ancienne présidente régionale Auvergne-Rhône-Alpes (2017-2025).",
                publicRoles: [
                    {
                        role: "Présidente déléguée régionale",
                        organization: "Croix-Rouge Auvergne-Rhône-Alpes",
                        start_date: "2017",
                        end_date: "2025",
                        status: "Former"
                    }
                ],
                conflictOfInterest: false
            },
            { 
                name: "Philippe Da Costa", 
                role: "Ancien Président", 
                source: "Site officiel Croix-Rouge",
                source_url: "https://www.croix-rouge.fr",
                date_verified: "2021",
                reliability: "high",
                note: "Président de 2021 à 2025",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel Croix-Rouge française",
        data_source_url: "https://www.croix-rouge.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "CROIX ROUGE": {
        board_members: [
            { 
                name: "Caroline Cross", 
                role: "Présidente", 
                source: "Site officiel Croix-Rouge",
                source_url: "https://www.croix-rouge.fr",
                date_verified: "2025-06-27",
                reliability: "high",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel Croix-Rouge",
        data_source_url: "https://www.croix-rouge.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "EMMAUS SOLIDARITE": {
        board_members: [
            { 
                name: "Véronique Petit", 
                role: "Directrice des Ressources Humaines", 
                source: "Données publiques, Pappers",
                source_url: null,
                date_verified: "2026-04-01",
                reliability: "medium",
                note: "Partie du groupe Emmaus",
                publicRoles: [],
                conflictOfInterest: false
            },
            { 
                name: "Conseil d'administration", 
                role: "Instance de gouvernance", 
                source: "Structure association",
                source_url: null,
                date_verified: "2026-04-01",
                reliability: "low",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Données publiques, Registres",
        data_source_url: "https://emmaus-solidarite.org",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "ASSOCIATION POUR LE SOUTIEN DU THEATRE PRIVE": {
        board_members: [
            { 
                name: "Pascal Guillaume", 
                role: "Président", 
                source: "Site officiel ASTP, Théâtre Tristan Bernard",
                source_url: "https://astp.asso.fr",
                date_verified: "2024-10",
                reliability: "high",
                note: "Réélu octobre 2024. Directeur du Théâtre Tristan Bernard, co-directeur avec Béatrice Vignal.",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel ASTP",
        data_source_url: "https://astp.asso.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "ASTP": {
        board_members: [
            { 
                name: "Pascal Guillaume", 
                role: "Président", 
                source: "Site officiel ASTP",
                source_url: "https://astp.asso.fr",
                date_verified: "2024-10",
                reliability: "high",
                note: "Réélu octobre 2024",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Site officiel ASTP",
        data_source_url: "https://astp.asso.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    },
    "THEATRE DU CHATELET": {
        board_members: [
            { 
                name: "Thomas Lauriot dit Prévost", 
                role: "Directeur général", 
                source: "Presse 2020 (Le Monde, Libération)",
                source_url: "https://www.lemonde.fr",
                date_verified: "2020",
                reliability: "high",
                publicRoles: [],
                conflictOfInterest: false
            },
            { 
                name: "Ruth Mackenzie", 
                role: "Ancienne Directrice artistique", 
                source: "Presse 2020",
                source_url: null,
                date_verified: "2020",
                reliability: "high",
                note: "Limogée en 2020",
                publicRoles: [],
                conflictOfInterest: false
            }
        ],
        data_source: "Presse",
        data_source_url: "https://www.lemonde.fr",
        last_updated: "2026-04-01",
        coverage: "partial"
    }
};

// Source documentation report
const SOURCE_DOCUMENTATION = {
    generated_at: "2026-04-01",
    associations_covered: 12,
    data_sources: {
        official_websites: [
            { name: "Théâtre de la Ville", url: "https://www.theatredelaville-paris.com", reliability: "high" },
            { name: "AGOSPAP", url: "https://www.agospap.fr", reliability: "high" },
            { name: "Forum des Images", url: "https://www.forumdesimages.fr", reliability: "high" },
            { name: "Orchestre de chambre de Paris", url: "https://www.orchestredechambredeparis.com", reliability: "high" },
            { name: "Croix-Rouge française", url: "https://www.croix-rouge.fr", reliability: "high" },
            { name: "Emmaus Solidarité", url: "https://emmaus-solidarite.org", reliability: "high" },
            { name: "ASTP", url: "https://astp.asso.fr", reliability: "high" },
            { name: "Philharmonie de Paris", url: "https://philharmoniedeparis.fr", reliability: "high" }
        ],
        public_registries: [
            { name: "Service Public - Annuaire", url: "https://lannuaire.service-public.gouv.fr", reliability: "high" },
            { name: "Pappers.fr", url: "https://www.pappers.fr", reliability: "medium" },
            { name: "Societe.com", url: "https://www.societe.com", reliability: "medium" }
        ],
        press_sources: [
            { name: "Le Monde", url: "https://www.lemonde.fr", reliability: "high" },
            { name: "Le Figaro", url: "https://www.lefigaro.fr", reliability: "high" },
            { name: "Libération", url: "https://www.liberation.fr", reliability: "high" },
            { name: "Sud Ouest", url: "https://www.sudouest.fr", reliability: "high" }
        ],
        government_sources: [
            { name: "Ministère de la Culture", url: "https://www.culture.gouv.fr", reliability: "high" },
            { name: "Presse.paris.fr", url: "https://presse.paris.fr", reliability: "high" },
            { name: "LesBiographies.com", url: "https://www.lesbiographies.com", reliability: "medium" }
        ],
        encyclopedic: [
            { name: "Wikipédia FR", url: "https://fr.wikipedia.org", reliability: "medium" },
            { name: "Wikipédia EN", url: "https://en.wikipedia.org", reliability: "medium" }
        ]
    },
    reliability_levels: {
        high: "Données confirmées par source officielle ou plusieurs sources indépendantes",
        medium: "Données provenant de sources professionnelles ou spécialisées",
        low: "Données partielles ou non vérifiées"
    },
    conflict_of_interest_summary: {
        total_checked: 12,
        potential_conflicts: 1,
        conflict_details: [
            {
                association: "AGOSPAP",
                member: "Jean-Paul Brandela",
                role: "Président",
                conflict_type: "Former high-ranking Paris city official",
                description: "Ancien Administrateur général de la Ville de Paris, Directeur adjoint de la démocratie"
            }
        ]
    }
};

// Function to find board members for an association
function findBoardMembers(associationName) {
    // Try exact match first
    if (BOARD_MEMBERS_DB_ENHANCED[associationName]) {
        return BOARD_MEMBERS_DB_ENHANCED[associationName];
    }
    
    // Try case-insensitive partial match
    const upperName = associationName.toUpperCase();
    for (const [key, data] of Object.entries(BOARD_MEMBERS_DB_ENHANCED)) {
        if (upperName.includes(key.toUpperCase()) || key.toUpperCase().includes(upperName)) {
            return data;
        }
    }
    
    return null;
}

// Function to check if association has potential conflicts
function hasConflictOfInterest(associationName) {
    const boardData = findBoardMembers(associationName);
    if (!boardData || !boardData.board_members) return false;
    
    return boardData.board_members.some(member => member.conflictOfInterest);
}

// Function to generate expandable board member card HTML
function generateBoardMemberCardHTML(member, index) {
    const hasConflict = member.conflictOfInterest;
    const hasPublicRoles = member.publicRoles && member.publicRoles.length > 0;
    const hasSourceURL = member.source_url && member.source_url !== null;
    
    const reliabilityBadge = {
        'high': '🔒',
        'medium': '🔓',
        'low': '⚠️'
    }[member.reliability] || '❓';
    
    const reliabilityText = {
        'high': 'Source vérifiée',
        'medium': 'Source professionnelle',
        'low': 'Source à vérifier'
    }[member.reliability] || 'Fiabilité inconnue';
    
    return `
        <div class="board-member-card-enhanced" data-member-index="${index}">
            <div class="board-member-header" onclick="toggleBoardMemberCard(${index})">
                <div class="board-member-title-row">
                    <div class="board-member-name">${escapeHtml(member.name)}</div>
                    ${hasConflict ? '<span class="conflict-badge" title="Potentiel conflit d\'intérêts">⚠️</span>' : ''}
                </div>
                <div class="board-member-role">${escapeHtml(member.role)}</div>
                ${member.note ? `<div class="board-member-note-preview">${escapeHtml(member.note.substring(0, 60))}${member.note.length > 60 ? '...' : ''}</div>` : ''}
                <div class="board-member-footer-row">
                    <span class="source-btn">📋 Source</span>
                    <span class="reliability-indicator" title="${reliabilityText}">${reliabilityBadge}</span>
                </div>
            </div>
            <div class="board-member-expanded" id="board-member-expanded-${index}" style="display: none;">
                <div class="expanded-content">
                    ${member.note ? `
                        <div class="expanded-section">
                            <div class="expanded-label">Note</div>
                            <div class="expanded-value">${escapeHtml(member.note)}</div>
                        </div>
                    ` : ''}
                    
                    <div class="expanded-section source-section">
                        <div class="expanded-label">📚 Source de l'information</div>
                        <div class="expanded-value">
                            <div class="source-name">${escapeHtml(member.source)}</div>
                            ${hasSourceURL ? `<a href="${member.source_url}" target="_blank" class="source-link" rel="noopener">Voir la source ↗</a>` : '<span class="source-unavailable">Lien non disponible</span>'}
                            <div class="source-meta">
                                <span>Vérifié le: ${member.date_verified || 'Non daté'}</span>
                                <span class="reliability-tag reliability-${member.reliability}">${reliabilityText}</span>
                            </div>
                        </div>
                    </div>
                    
                    ${hasPublicRoles ? `
                        <div class="expanded-section public-roles-section">
                            <div class="expanded-label">🏛️ Mandats publics</div>
                            <div class="expanded-value">
                                ${member.publicRoles.map(role => `
                                    <div class="public-role-item">
                                        <div class="public-role-title">${escapeHtml(role.role)}</div>
                                        <div class="public-role-org">${escapeHtml(role.organization)}</div>
                                        <div class="public-role-dates">
                                            ${role.start_date || '?'} - ${role.end_date || 'présent'}
                                            ${role.status ? `<span class="public-role-status">(${role.status})</span>` : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${hasConflict ? `
                        <div class="expanded-section conflict-section">
                            <div class="expanded-label">⚠️ Alerte conflit d'intérêts</div>
                            <div class="expanded-value">
                                <div class="conflict-warning">
                                    <strong>Potentiel conflit détecté</strong>
                                    <p>${escapeHtml(member.conflictReason || 'Ce membre a occupé des fonctions publiques susceptibles de créer un conflit d\'intérêts.')}</p>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Function to generate complete board members section HTML
function generateBoardMembersHTML(associationName) {
    const boardData = findBoardMembers(associationName);
    const hasConflict = hasConflictOfInterest(associationName);
    
    if (!boardData || !boardData.board_members || boardData.board_members.length === 0) {
        return `
            <div class="board-members-section-enhanced">
                <h3><span class="icon">👥</span> Membres du Bureau</h3>
                <div class="board-members-content">
                    <p class="no-data">Données non disponibles</p>
                    <p class="data-source">Source: En cours de recherche</p>
                </div>
            </div>
        `;
    }
    
    const membersHTML = boardData.board_members.map((member, index) => 
        generateBoardMemberCardHTML(member, index)
    ).join('');
    
    const conflictBanner = hasConflict ? `
        <div class="conflict-banner">
            <span class="conflict-icon">⚠️</span>
            <span class="conflict-text">Cette association comporte un potentiel conflit d'intérêts</span>
        </div>
    ` : '';
    
    return `
        <div class="board-members-section-enhanced">
            <h3><span class="icon">👥</span> Membres du Bureau / Conseil d'Administration</h3>
            ${conflictBanner}
            <div class="board-members-grid-enhanced">
                ${membersHTML}
            </div>
            <div class="data-source-enhanced">
                <div class="source-row">
                    <span class="source-label">📚 Source principale:</span>
                    <span class="source-value">${escapeHtml(boardData.data_source)}</span>
                    ${boardData.data_source_url ? `<a href="${boardData.data_source_url}" target="_blank" class="source-external-link" rel="noopener">↗</a>` : ''}
                </div>
                <div class="source-row">
                    <span class="source-label">📅 Mis à jour:</span>
                    <span class="source-value">${boardData.last_updated}</span>
                </div>
                <div class="source-row">
                    <span class="source-label">📊 Couverture:</span>
                    <span class="coverage-tag coverage-${boardData.coverage}">
                        ${boardData.coverage === 'complete' ? 'Complète' : boardData.coverage === 'partial' ? 'Partielle' : 'Minimale'}
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Function to toggle board member card expansion
function toggleBoardMemberCard(index) {
    const expandedSection = document.getElementById(`board-member-expanded-${index}`);
    const card = expandedSection.closest('.board-member-card-enhanced');
    
    if (expandedSection.style.display === 'none') {
        expandedSection.style.display = 'block';
        card.classList.add('expanded');
        // Smooth animation
        expandedSection.style.maxHeight = expandedSection.scrollHeight + 'px';
    } else {
        expandedSection.style.maxHeight = '0';
        setTimeout(() => {
            expandedSection.style.display = 'none';
            card.classList.remove('expanded');
        }, 300);
    }
}

// Function to add board members section to modal
function addBoardMembersToModal(modalContent, association) {
    const boardHTML = generateBoardMembersHTML(association.name);
    
    // Insert before the last section or at the end
    const lastSection = modalContent.querySelector('.modal-section:last-child');
    if (lastSection) {
        const boardSection = document.createElement('div');
        boardSection.className = 'modal-section board-section-enhanced';
        boardSection.innerHTML = boardHTML;
        lastSection.parentNode.insertBefore(boardSection, lastSection.nextSibling);
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        findBoardMembers, 
        generateBoardMembersHTML, 
        addBoardMembersToModal,
        hasConflictOfInterest,
        SOURCE_DOCUMENTATION,
        BOARD_MEMBERS_DB_ENHANCED
    };
}
