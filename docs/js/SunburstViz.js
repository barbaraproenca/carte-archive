/**
 * SunburstViz - Visualisation Sunburst interactive avec Plotly
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
export class SunburstViz {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.options = {
      onNodeClick: options.onNodeClick || null,
      ...options
    };
  }

  /**
   * Rend le sunburst avec les donnees fournies
   */
  render(data) {
    this.data = data;

    const containerHeight = this.container.clientHeight || 600;
    const containerWidth = this.container.clientWidth || 800;

    // Construire les labels avec titre pour les inventaires
    const displayLabels = data.customdata.map((cd, i) => {
      if (cd.type === 'inventaire') {
        // Pour les inventaires : cote + debut du titre
        const titre = cd.titre || '';
        const shortTitre = titre.length > 25 ? titre.substring(0, 25) + '...' : titre;
        return `${data.labels[i]}<br><span style="font-size:10px">${shortTitre}</span>`;
      }
      return data.labels[i];
    });

    const trace = {
      type: 'sunburst',
      ids: data.ids,
      labels: data.labels,
      parents: data.parents,
      values: data.values,
      customdata: data.customdata,
      
      branchvalues: 'remainder',
      
      marker: {
        colors: data.colors,
        line: {
          width: 1,
          color: 'rgba(15, 15, 26, 0.5)'
        }
      },
      
      textfont: {
        family: 'JetBrains Mono, monospace',
        size: 11,
        color: 'white'
      },
      
      insidetextorientation: 'radial',
      
      hovertemplate: this.getHoverTemplate(),
      
      leaf: {
        opacity: 0.9
      },
      
      maxdepth: 3
    };

    const layout = {
      height: containerHeight,
      width: containerWidth,
      margin: { t: 10, l: 10, r: 10, b: 10 },
      font: {
        family: 'JetBrains Mono, monospace',
        color: '#f1f5f9'
      },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      sunburstcolorway: data.colors
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      displaylogo: false,
      toImageButtonOptions: {
        format: 'png',
        filename: 'archives_ad13_sunburst',
        height: 1200,
        width: 1200,
        scale: 2
      }
    };

    Plotly.newPlot(this.containerId, [trace], layout, config);

    // Gestion du clic - ouvrir le lien directement pour les inventaires
    this.container.on('plotly_click', (eventData) => {
      if (eventData.points && eventData.points[0]) {
        const point = eventData.points[0];
        const customdata = point.customdata || {};
        
        // Si c'est un inventaire avec une URL, ouvrir dans un nouvel onglet
        if (customdata.type === 'inventaire' && customdata.url) {
          window.open(customdata.url, '_blank');
        } else if (customdata.url) {
          // Pour les autres niveaux, ouvrir aussi
          window.open(customdata.url, '_blank');
        }
        
        if (this.options.onNodeClick) {
          this.options.onNodeClick({
            id: point.id,
            label: point.label,
            value: point.value,
            customdata
          });
        }
      }
    });
  }

  /**
   * Template pour le hover - affiche description et stats
   */
  getHoverTemplate() {
    return `
<b style="font-size:14px">%{label}</b><br>
<br>
%{customdata.hoverText}<br>
<br>
<span style="color:#10B981">%{customdata.statsText}</span><br>
<extra>Cliquer pour ouvrir</extra>
    `.trim();
  }

  /**
   * Redimensionne le graphique
   */
  resize() {
    const containerHeight = this.container.clientHeight || 600;
    const containerWidth = this.container.clientWidth || 800;
    
    Plotly.relayout(this.containerId, {
      height: containerHeight,
      width: containerWidth
    });
  }
}

