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
          width: 1.5,
          color: 'rgba(15, 15, 26, 0.6)'
        },
        pad: {
          t: 28,
          l: 6,
          r: 6,
          b: 6
        }
      },
      
      textfont: {
        family: 'JetBrains Mono, monospace',
        size: 12,
        color: 'white'
      },
      
      hovertemplate: this.getHoverTemplate(),
      
      pathbar: {
        visible: this.options.showBreadcrumb,
        thickness: 26,
        textfont: {
          family: 'JetBrains Mono, monospace',
          size: 11,
          color: '#1a1a2e'
        },
        side: 'top'
      },
      
      maxdepth: 3
    };

    const layout = {
      height: this.options.height,
      margin: { t: 40, l: 5, r: 5, b: 5 },
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

    // Gerer les clics
    this.container.on('plotly_click', (eventData) => {
      if (eventData.points && eventData.points[0]) {
        const point = eventData.points[0];
        if (this.options.onNodeClick) {
          this.options.onNodeClick({
            id: point.id,
            label: point.label,
            value: point.value,
            customdata: point.customdata
          });
        }
      }
    });
  }

  /**
   * Template pour le hover
   */
  getHoverTemplate() {
    return `<b>%{label}</b><extra></extra>`;
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
