/**
 * TreeViz - Arbre collapsible avec D3.js
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
export class TreeViz {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.options = {
      width: options.width || 1200,
      height: options.height || 800,
      nodeRadius: options.nodeRadius || 8,
      duration: options.duration || 500,
      onNodeClick: options.onNodeClick || null,
      ...options
    };
    
    this.margin = { top: 40, right: 200, bottom: 40, left: 200 };
    this.nodeId = 0;
  }

  /**
   * Rend l'arbre avec les donnees fournies
   */
  render(data) {
    this.data = data;
    
    this.container.innerHTML = '';
    
    const containerRect = this.container.getBoundingClientRect();
    const actualWidth = containerRect.width || this.options.width;
    const actualHeight = containerRect.height || this.options.height;
    
    const width = actualWidth - this.margin.left - this.margin.right;
    const height = actualHeight - this.margin.top - this.margin.bottom;

    this.svg = d3.select(`#${this.containerId}`)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${actualWidth} ${actualHeight}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .append('g')
      .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

    this.treeLayout = d3.tree().size([height, width]);

    this.root = d3.hierarchy(data);
    this.root.x0 = height / 2;
    this.root.y0 = 0;

    if (this.root.children) {
      this.root.children.forEach(child => this.collapse(child));
    }

    this.update(this.root);
  }

  /**
   * Collapse un noeud et ses enfants
   */
  collapse(node) {
    if (node.children) {
      node._children = node.children;
      node._children.forEach(child => this.collapse(child));
      node.children = null;
    }
  }

  /**
   * Expand un noeud
   */
  expand(node) {
    if (node._children) {
      node.children = node._children;
      node._children = null;
    }
  }

  /**
   * Toggle un noeud
   */
  toggle(node) {
    if (node.children) {
      node._children = node.children;
      node.children = null;
    } else if (node._children) {
      node.children = node._children;
      node._children = null;
    }
  }

  /**
   * Met a jour l'arbre
   */
  update(source) {
    const duration = this.options.duration;

    const treeData = this.treeLayout(this.root);
    const nodes = treeData.descendants();
    const links = treeData.links();

    nodes.forEach(d => {
      d.y = d.depth * 250;
    });

    const node = this.svg.selectAll('g.node')
      .data(nodes, d => d.id || (d.id = ++this.nodeId));

    const nodeEnter = node.enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${source.y0},${source.x0})`)
      .on('click', (event, d) => {
        this.toggle(d);
        this.update(d);
        if (this.options.onNodeClick) {
          this.options.onNodeClick(d.data);
        }
      });

    nodeEnter.append('circle')
      .attr('r', 1e-6)
      .attr('class', d => d._children ? 'node-circle has-children' : 'node-circle')
      .style('fill', d => this.getNodeColor(d))
      .style('stroke', d => d3.rgb(this.getNodeColor(d)).darker(0.5))
      .style('stroke-width', 2)
      .style('cursor', 'pointer');

    nodeEnter.append('text')
      .attr('dy', '.35em')
      .attr('x', d => d.children || d._children ? -15 : 15)
      .attr('text-anchor', d => d.children || d._children ? 'end' : 'start')
      .text(d => this.truncateLabel(d.data.name, 40))
      .style('font-family', 'JetBrains Mono, monospace')
      .style('font-size', '12px')
      .style('fill', '#e2e8f0')
      .style('cursor', 'pointer')
      .clone(true).lower()
      .attr('stroke', '#1a1a2e')
      .attr('stroke-width', 3);

    const nodeUpdate = nodeEnter.merge(node);

    nodeUpdate.transition()
      .duration(duration)
      .attr('transform', d => `translate(${d.y},${d.x})`);

    nodeUpdate.select('circle')
      .attr('r', this.options.nodeRadius)
      .attr('class', d => d._children ? 'node-circle has-children' : 'node-circle')
      .style('fill', d => d._children ? this.getNodeColor(d) : 
                          d.children ? d3.rgb(this.getNodeColor(d)).brighter(0.3) : 
                          this.getNodeColor(d));

    const nodeExit = node.exit()
      .transition()
      .duration(duration)
      .attr('transform', d => `translate(${source.y},${source.x})`)
      .remove();

    nodeExit.select('circle')
      .attr('r', 1e-6);

    nodeExit.select('text')
      .style('fill-opacity', 1e-6);

    const link = this.svg.selectAll('path.link')
      .data(links, d => d.target.id);

    const linkEnter = link.enter()
      .insert('path', 'g')
      .attr('class', 'link')
      .attr('d', d => {
        const o = { x: source.x0, y: source.y0 };
        return this.diagonal(o, o);
      })
      .style('fill', 'none')
      .style('stroke', '#4a5568')
      .style('stroke-width', 1.5)
      .style('opacity', 0.6);

    const linkUpdate = linkEnter.merge(link);

    linkUpdate.transition()
      .duration(duration)
      .attr('d', d => this.diagonal(d.source, d.target));

    link.exit()
      .transition()
      .duration(duration)
      .attr('d', d => {
        const o = { x: source.x, y: source.y };
        return this.diagonal(o, o);
      })
      .remove();

    nodes.forEach(d => {
      d.x0 = d.x;
      d.y0 = d.y;
    });
  }

  /**
   * Genere le chemin diagonal entre deux points
   */
  diagonal(s, d) {
    return `M ${s.y} ${s.x}
            C ${(s.y + d.y) / 2} ${s.x},
              ${(s.y + d.y) / 2} ${d.x},
              ${d.y} ${d.x}`;
  }

  /**
   * Retourne la couleur d'un noeud selon sa profondeur
   */
  getNodeColor(d) {
    const colors = [
      '#6366F1',
      '#F59E0B',
      '#10B981',
      '#8B5CF6',
      '#EC4899'
    ];
    return colors[Math.min(d.depth, colors.length - 1)];
  }

  /**
   * Tronque un label s'il est trop long
   */
  truncateLabel(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }

  /**
   * Expand tous les noeuds
   */
  expandAll() {
    const expandRecursive = (node) => {
      if (node._children) {
        node.children = node._children;
        node._children = null;
      }
      if (node.children) {
        node.children.forEach(expandRecursive);
      }
    };
    expandRecursive(this.root);
    this.update(this.root);
  }

  /**
   * Collapse tous les noeuds
   */
  collapseAll() {
    if (this.root.children) {
      this.root.children.forEach(child => this.collapse(child));
    }
    this.update(this.root);
  }

  /**
   * Centre la vue sur un noeud specifique
   */
  centerOnNode(node) {
    // Implementation future
  }
}
