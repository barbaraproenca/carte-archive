/**
 * TreemapViz - Visualisation Treemap interactive avec Plotly
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
export class TreemapViz {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.options = {
      height: options.height || 700,
      showBreadcrumb: options.showBreadcrumb !== false,
      onNodeClick: options.onNodeClick || null,
      ...options
    };
    this.currentPath = [];
  }

  /**
   * Rend le treemap avec les donnees fournies
   */
  render(data) {
    this.data = data;

    const containerHeight = this.container.clientHeight || this.options.height;
    this.options.height = containerHeight;

    const trace = {
      type: 'treemap',
      ids: data.ids,
      labels: data.labels,
      parents: data.parents,
      values: data.values,
      customdata: data.customdata,
      
      branchvalues: 'remainder',
      textinfo: 'label+percent parent',
      
      marker: {
        colors: data.colors,
        line: {
          width: 2,
          color: 'white'
        },
        pad: {
          t: 30,
          l: 10,
          r: 10,
          b: 10
        }
      },
      
      textfont: {
        family: 'JetBrains Mono, monospace',
        size: 14,
        color: 'white'
      },
      
      hovertemplate: this.getHoverTemplate(),
      
      pathbar: {
        visible: this.options.showBreadcrumb,
        thickness: 30,
        textfont: {
          family: 'JetBrains Mono, monospace',
          size: 13,
          color: '#1a1a2e'
        },
        side: 'top'
      },
      
      maxdepth: 2
    };

    const layout = {
      height: this.options.height,
      margin: { t: 50, l: 10, r: 10, b: 10 },
      font: {
        family: 'JetBrains Mono, monospace',
        color: '#f1f5f9'
      },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)'
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      displaylogo: false,
      toImageButtonOptions: {
        format: 'png',
        filename: 'archives_ad13_treemap',
        height: 1200,
        width: 1600,
        scale: 2
      }
    };

    Plotly.newPlot(this.containerId, [trace], layout, config);

    this.container.on('plotly_click', (eventData) => {
      if (eventData.points && eventData.points[0]) {
        const point = eventData.points[0];
        this.handleClick(point);
      }
    });

    this.container.on('plotly_treemapclick', (eventData) => {
      if (this.options.onNodeClick) {
        this.options.onNodeClick(eventData);
      }
    });
  }

  /**
   * Template pour le hover
   */
  getHoverTemplate() {
    return `
<b>%{label}</b><br>
<br>
Metrage: %{customdata.metrage:.2f} ml<br>
Entrees: %{customdata.nombreEntrees}<br>
Dates: %{customdata.dateExtreme}<br>
<extra></extra>
    `.trim();
  }

  /**
   * Gere le clic sur un noeud
   */
  handleClick(point) {
    const customdata = point.customdata;
    this.updateInfoPanel(point);

    if (this.options.onNodeClick) {
      this.options.onNodeClick({
        id: point.id,
        label: point.label,
        value: point.value,
        customdata
      });
    }
  }

  /**
   * Met a jour le panneau d'information
   */
  updateInfoPanel(point) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;

    const customdata = point.customdata || {};
    const type = customdata.type || 'unknown';
    
    const badge = document.getElementById('info-badge');
    if (badge) badge.textContent = this.getTypeBadge(type);
    
    const title = document.getElementById('info-title');
    if (title) title.textContent = point.label;
    
    const desc = document.getElementById('info-description');
    if (desc) desc.textContent = customdata.description || 'Aucune description disponible.';
    
    const statsContainer = document.getElementById('info-stats-container');
    if (statsContainer) {
      let statsHtml = `
        <div class="stat">
          <span class="stat-value">${(customdata.metrage || 0).toFixed(2)}</span>
          <span class="stat-label">metres lineaires</span>
        </div>
        <div class="stat">
          <span class="stat-value">${customdata.nombreEntrees || 0}</span>
          <span class="stat-label">versements</span>
        </div>
      `;
      if (customdata.nombreProducteurs) {
        statsHtml += `
          <div class="stat">
            <span class="stat-value">${customdata.nombreProducteurs}</span>
            <span class="stat-label">producteurs</span>
          </div>
        `;
      }
      statsContainer.innerHTML = statsHtml;
    }
    
    const dates = document.getElementById('info-dates');
    if (dates) dates.textContent = `Dates extremes: ${customdata.dateExtreme || '-'}`;

    // Afficher le lien vers le site AD13 si disponible
    const link = document.getElementById('info-link');
    if (link) {
      if (customdata.url) {
        link.href = customdata.url;
        link.classList.remove('hidden');
      } else {
        link.classList.add('hidden');
      }
    }

    // Afficher le lien de recherche dans les inventaires
    const searchLink = document.getElementById('info-search-link');
    if (searchLink) {
      if (customdata.urlRecherche) {
        searchLink.href = customdata.urlRecherche;
        searchLink.classList.remove('hidden');
      } else {
        searchLink.classList.add('hidden');
      }
    }

    infoPanel.classList.add('visible');
  }

  /**
   * Retourne le badge pour le type
   */
  getTypeBadge(type) {
    const badges = {
      'root': 'Racine',
      'fonction': 'Fonction',
      'thematique': 'Thematique',
      'producteur': 'Producteur'
    };
    return badges[type] || 'Element';
  }

  /**
   * Redimensionne le graphique
   */
  resize() {
    Plotly.Plots.resize(this.container);
  }

  /**
   * Met a jour les donnees
   */
  update(data) {
    this.data = data;
    Plotly.react(this.containerId, [{
      type: 'treemap',
      ids: data.ids,
      labels: data.labels,
      parents: data.parents,
      values: data.values,
      customdata: data.customdata,
      marker: { colors: data.colors }
    }]);
  }

  /**
   * Exporte le graphique en image
   */
  async exportImage(format = 'png') {
    return await Plotly.downloadImage(this.container, {
      format,
      width: 1600,
      height: 1200,
      filename: 'archives_ad13_treemap'
    });
  }
}
