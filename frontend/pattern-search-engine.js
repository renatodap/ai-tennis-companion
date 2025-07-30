/**
 * 🔍 NATURAL LANGUAGE PATTERN SEARCH ENGINE
 * "Show me all backhands under pressure in set 2"
 */

class TennisPatternSearchEngine {
    constructor() {
        this.strokeData = [];
        this.rallyData = [];
        this.searchHistory = [];
        this.patterns = new Map();
        
        // Define search patterns and their handlers
        this.searchPatterns = [
            {
                pattern: /show me (?:all )?(\w+) (?:shots?|strokes?) (?:in|during) (.+)/i,
                handler: this.searchStrokesByContext.bind(this)
            },
            {
                pattern: /(?:find|show) (?:all )?(\w+) under pressure/i,
                handler: this.searchStrokesUnderPressure.bind(this)
            },
            {
                pattern: /what (?:do|did) i hit (?:when|at) (.+)/i,
                handler: this.searchStrokesByGameState.bind(this)
            },
            {
                pattern: /(?:how many|count) (\w+) (?:shots?|strokes?)/i,
                handler: this.countStrokes.bind(this)
            },
            {
                pattern: /(?:analyze|show) rally (\d+)/i,
                handler: this.analyzeSpecificRally.bind(this)
            },
            {
                pattern: /(?:where|position) (?:do|did) i (?:hit|play) (\w+)/i,
                handler: this.searchStrokePositions.bind(this)
            },
            {
                pattern: /(?:errors?|mistakes?) (?:in|during) (.+)/i,
                handler: this.searchErrors.bind(this)
            },
            {
                pattern: /(?:winners?|winning shots?) (?:in|during) (.+)/i,
                handler: this.searchWinners.bind(this)
            }
        ];
        
        this.init();
    }
    
    init() {
        this.createSearchInterface();
        this.setupEventListeners();
        this.loadSampleQueries();
    }
    
    createSearchInterface() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'pattern-search-container';
        searchContainer.innerHTML = `
            <div class="search-header">
                <h3>🔍 Ask About Your Tennis</h3>
                <p>Natural language search - ask anything about your game!</p>
            </div>
            
            <div class="search-input-container">
                <input type="text" 
                       class="search-input" 
                       id="patternSearchInput"
                       placeholder="e.g., 'Show me all forehands under pressure' or 'How many winners in set 2?'"
                       autocomplete="off">
                <button class="search-btn" id="searchBtn">Search</button>
            </div>
            
            <div class="sample-queries">
                <div class="sample-queries-header">Try these examples:</div>
                <div class="sample-query-tags" id="sampleQueries"></div>
            </div>
            
            <div class="search-results" id="searchResults"></div>
            
            <div class="search-history" id="searchHistory">
                <div class="history-header">Recent Searches</div>
                <div class="history-items"></div>
            </div>
        `;
        
        return searchContainer;
    }
    
    setupEventListeners() {
        // This will be called when the search interface is added to DOM
        document.addEventListener('DOMContentLoaded', () => {
            this.bindEvents();
        });
    }
    
    bindEvents() {
        const searchInput = document.getElementById('patternSearchInput');
        const searchBtn = document.getElementById('searchBtn');
        const sampleQueries = document.getElementById('sampleQueries');
        
        if (searchInput && searchBtn) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.executeSearch(searchInput.value);
                }
            });
            
            searchBtn.addEventListener('click', () => {
                this.executeSearch(searchInput.value);
            });
            
            // Auto-complete suggestions
            searchInput.addEventListener('input', (e) => {
                this.showSuggestions(e.target.value);
            });
        }
        
        if (sampleQueries) {
            sampleQueries.addEventListener('click', (e) => {
                if (e.target.classList.contains('sample-query')) {
                    const query = e.target.textContent;
                    searchInput.value = query;
                    this.executeSearch(query);
                }
            });
        }
    }
    
    loadSampleQueries() {
        const samples = [
            "Show me all forehands under pressure",
            "How many winners in the match?",
            "Where do I hit backhands?",
            "Analyze rally 5",
            "What do I hit at 30-40?",
            "Errors in the second set",
            "Show me serves to the T",
            "Crosscourt shots percentage"
        ];
        
        const container = document.getElementById('sampleQueries');
        if (container) {
            container.innerHTML = samples.map(query => 
                `<span class="sample-query">${query}</span>`
            ).join('');
        }
    }
    
    loadData(strokeData, rallyData = []) {
        this.strokeData = strokeData || [];
        this.rallyData = rallyData || [];
        this.buildSearchIndex();
    }
    
    buildSearchIndex() {
        // Build search index for faster queries
        this.patterns.clear();
        
        // Index by stroke type
        this.strokeData.forEach((stroke, index) => {
            const type = stroke.stroke_type?.toLowerCase();
            if (type) {
                if (!this.patterns.has(type)) {
                    this.patterns.set(type, []);
                }
                this.patterns.get(type).push({ ...stroke, index });
            }
        });
        
        // Index by pressure situations
        const pressureStrokes = this.strokeData.filter(s => s.pressure_index > 0.7);
        this.patterns.set('pressure', pressureStrokes);
        
        // Index by outcomes
        const winners = this.strokeData.filter(s => s.outcome === 'winner');
        const errors = this.strokeData.filter(s => s.outcome === 'error');
        this.patterns.set('winners', winners);
        this.patterns.set('errors', errors);
    }
    
    executeSearch(query) {
        if (!query.trim()) return;
        
        const results = this.processNaturalLanguageQuery(query);
        this.displayResults(query, results);
        this.addToHistory(query, results);
    }
    
    processNaturalLanguageQuery(query) {
        const normalizedQuery = query.toLowerCase().trim();
        
        // Try to match against known patterns
        for (const { pattern, handler } of this.searchPatterns) {
            const match = normalizedQuery.match(pattern);
            if (match) {
                return handler(match, normalizedQuery);
            }
        }
        
        // Fallback: keyword-based search
        return this.performKeywordSearch(normalizedQuery);
    }
    
    searchStrokesByContext(match, query) {
        const strokeType = match[1].toLowerCase();
        const context = match[2].toLowerCase();
        
        let strokes = this.patterns.get(strokeType) || [];
        
        // Filter by context
        if (context.includes('pressure')) {
            strokes = strokes.filter(s => s.pressure_index > 0.7);
        } else if (context.includes('set 1')) {
            strokes = strokes.filter(s => s.set_number === 1);
        } else if (context.includes('set 2')) {
            strokes = strokes.filter(s => s.set_number === 2);
        }
        
        return {
            type: 'stroke_list',
            title: `${strokeType.charAt(0).toUpperCase() + strokeType.slice(1)} shots ${context}`,
            data: strokes,
            summary: `Found ${strokes.length} ${strokeType} shots ${context}`,
            visualizations: ['timeline', 'heatmap']
        };
    }
    
    searchStrokesUnderPressure(match, query) {
        const strokeType = match[1].toLowerCase();
        let strokes = this.strokeData.filter(s => s.pressure_index > 0.7);
        
        if (strokeType !== 'all' && strokeType !== 'shots' && strokeType !== 'strokes') {
            strokes = strokes.filter(s => s.stroke_type?.toLowerCase() === strokeType);
        }
        
        const successRate = strokes.length > 0 ? 
            (strokes.filter(s => s.outcome !== 'error').length / strokes.length * 100).toFixed(1) : 0;
        
        return {
            type: 'pressure_analysis',
            title: `${strokeType.charAt(0).toUpperCase() + strokeType.slice(1)} under pressure`,
            data: strokes,
            summary: `Found ${strokes.length} shots under pressure with ${successRate}% success rate`,
            insights: [
                `You hit ${strokes.length} ${strokeType} shots under pressure`,
                `Success rate: ${successRate}%`,
                `Most common outcome: ${this.getMostCommonOutcome(strokes)}`
            ],
            visualizations: ['timeline', 'pressure_chart']
        };
    }
    
    searchStrokesByGameState(match, query) {
        const gameState = match[1].toLowerCase();
        let strokes = this.strokeData;
        
        // Parse game state (e.g., "30-40", "deuce", "break point")
        if (gameState.includes('30-40') || gameState.includes('break point')) {
            strokes = strokes.filter(s => s.game_state?.includes('break_point'));
        } else if (gameState.includes('deuce')) {
            strokes = strokes.filter(s => s.game_state?.includes('deuce'));
        }
        
        const strokeTypes = this.getStrokeTypeDistribution(strokes);
        
        return {
            type: 'game_state_analysis',
            title: `Shots hit at ${gameState}`,
            data: strokes,
            summary: `Found ${strokes.length} shots at ${gameState}`,
            insights: [
                `Most common shot: ${strokeTypes[0]?.type || 'N/A'} (${strokeTypes[0]?.percentage || 0}%)`,
                `Total shots analyzed: ${strokes.length}`,
                `Pressure index: ${this.getAveragePressure(strokes).toFixed(2)}`
            ],
            visualizations: ['pie_chart', 'timeline']
        };
    }
    
    countStrokes(match, query) {
        const strokeType = match[1].toLowerCase();
        const strokes = this.patterns.get(strokeType) || [];
        
        const total = strokes.length;
        const winners = strokes.filter(s => s.outcome === 'winner').length;
        const errors = strokes.filter(s => s.outcome === 'error').length;
        const inPlay = total - winners - errors;
        
        return {
            type: 'count_analysis',
            title: `${strokeType.charAt(0).toUpperCase() + strokeType.slice(1)} count`,
            data: { total, winners, errors, inPlay },
            summary: `${total} total ${strokeType} shots`,
            insights: [
                `Total: ${total} shots`,
                `Winners: ${winners} (${((winners/total)*100).toFixed(1)}%)`,
                `Errors: ${errors} (${((errors/total)*100).toFixed(1)}%)`,
                `In play: ${inPlay} (${((inPlay/total)*100).toFixed(1)}%)`
            ],
            visualizations: ['bar_chart', 'outcome_pie']
        };
    }
    
    analyzeSpecificRally(match, query) {
        const rallyNumber = parseInt(match[1]);
        const rally = this.rallyData.find(r => r.rally_id === `rally_${rallyNumber.toString().padStart(3, '0')}`);
        
        if (!rally) {
            return {
                type: 'error',
                title: 'Rally not found',
                summary: `Rally ${rallyNumber} not found in the data`,
                data: null
            };
        }
        
        return {
            type: 'rally_analysis',
            title: `Rally ${rallyNumber} Analysis`,
            data: rally,
            summary: `Rally ${rallyNumber}: ${rally.stroke_count} shots, ${rally.duration.toFixed(1)}s duration`,
            insights: [
                `Duration: ${rally.duration.toFixed(1)} seconds`,
                `Shots: ${rally.stroke_count}`,
                `Winner: ${rally.winner}`,
                `Pressure score: ${rally.pressure_score.toFixed(2)}`
            ],
            visualizations: ['rally_timeline', 'shot_sequence']
        };
    }
    
    searchStrokePositions(match, query) {
        const strokeType = match[1].toLowerCase();
        const strokes = this.patterns.get(strokeType) || [];
        
        const positions = strokes.map(s => ({
            x: s.player_position?.[0] || 0.5,
            y: s.player_position?.[1] || 0.8,
            zone: s.court_zone
        }));
        
        const zoneDistribution = this.getZoneDistribution(strokes);
        
        return {
            type: 'position_analysis',
            title: `${strokeType.charAt(0).toUpperCase() + strokeType.slice(1)} positions`,
            data: { strokes, positions, zoneDistribution },
            summary: `Position analysis for ${strokes.length} ${strokeType} shots`,
            insights: [
                `Most common zone: ${zoneDistribution[0]?.zone || 'N/A'}`,
                `Zone coverage: ${zoneDistribution.length} different zones`,
                `Average court position: ${this.getAveragePosition(positions)}`
            ],
            visualizations: ['heatmap', 'zone_chart']
        };
    }
    
    searchErrors(match, query) {
        const context = match[1].toLowerCase();
        let errors = this.patterns.get('errors') || [];
        
        // Filter by context
        if (context.includes('set 1')) {
            errors = errors.filter(s => s.set_number === 1);
        } else if (context.includes('set 2')) {
            errors = errors.filter(s => s.set_number === 2);
        }
        
        const errorTypes = this.getStrokeTypeDistribution(errors);
        
        return {
            type: 'error_analysis',
            title: `Errors ${context}`,
            data: errors,
            summary: `Found ${errors.length} errors ${context}`,
            insights: [
                `Total errors: ${errors.length}`,
                `Most error-prone shot: ${errorTypes[0]?.type || 'N/A'}`,
                `Error rate: ${this.calculateErrorRate(errors)}%`
            ],
            visualizations: ['error_chart', 'timeline']
        };
    }
    
    searchWinners(match, query) {
        const context = match[1].toLowerCase();
        let winners = this.patterns.get('winners') || [];
        
        // Filter by context
        if (context.includes('set 1')) {
            winners = winners.filter(s => s.set_number === 1);
        } else if (context.includes('set 2')) {
            winners = winners.filter(s => s.set_number === 2);
        }
        
        const winnerTypes = this.getStrokeTypeDistribution(winners);
        
        return {
            type: 'winner_analysis',
            title: `Winners ${context}`,
            data: winners,
            summary: `Found ${winners.length} winners ${context}`,
            insights: [
                `Total winners: ${winners.length}`,
                `Best winning shot: ${winnerTypes[0]?.type || 'N/A'}`,
                `Winner rate: ${this.calculateWinnerRate(winners)}%`
            ],
            visualizations: ['winner_chart', 'heatmap']
        };
    }
    
    performKeywordSearch(query) {
        // Fallback keyword search
        const keywords = query.split(' ').filter(word => word.length > 2);
        const results = [];
        
        keywords.forEach(keyword => {
            if (this.patterns.has(keyword)) {
                results.push(...this.patterns.get(keyword));
            }
        });
        
        return {
            type: 'keyword_search',
            title: `Search results for "${query}"`,
            data: results,
            summary: `Found ${results.length} matches`,
            visualizations: ['list']
        };
    }
    
    displayResults(query, results) {
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;
        
        if (results.type === 'error') {
            resultsContainer.innerHTML = `
                <div class="search-error">
                    <h4>${results.title}</h4>
                    <p>${results.summary}</p>
                </div>
            `;
            return;
        }
        
        resultsContainer.innerHTML = `
            <div class="search-result-card">
                <div class="result-header">
                    <h4>${results.title}</h4>
                    <div class="result-summary">${results.summary}</div>
                </div>
                
                ${results.insights ? `
                    <div class="result-insights">
                        <h5>Key Insights:</h5>
                        <ul>
                            ${results.insights.map(insight => `<li>${insight}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="result-actions">
                    <button class="action-btn" onclick="this.showVisualization('${results.type}')">
                        📊 Visualize
                    </button>
                    <button class="action-btn" onclick="this.exportResults('${query}')">
                        💾 Export
                    </button>
                    <button class="action-btn" onclick="this.shareResults('${query}')">
                        🔗 Share
                    </button>
                </div>
            </div>
        `;
        
        // Trigger visualization if available
        if (results.visualizations && results.visualizations.length > 0) {
            this.createVisualization(results);
        }
    }
    
    createVisualization(results) {
        // This would integrate with the heatmap and other visualization components
        const event = new CustomEvent('tennisSearchResults', {
            detail: {
                type: results.type,
                data: results.data,
                visualizations: results.visualizations
            }
        });
        
        document.dispatchEvent(event);
    }
    
    addToHistory(query, results) {
        this.searchHistory.unshift({
            query,
            results,
            timestamp: new Date()
        });
        
        // Keep only last 10 searches
        if (this.searchHistory.length > 10) {
            this.searchHistory = this.searchHistory.slice(0, 10);
        }
        
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const historyContainer = document.querySelector('#searchHistory .history-items');
        if (!historyContainer) return;
        
        historyContainer.innerHTML = this.searchHistory.map(item => `
            <div class="history-item" onclick="this.executeSearch('${item.query}')">
                <div class="history-query">${item.query}</div>
                <div class="history-summary">${item.results.summary}</div>
                <div class="history-time">${this.formatTime(item.timestamp)}</div>
            </div>
        `).join('');
    }
    
    showSuggestions(input) {
        // Auto-complete suggestions based on input
        const suggestions = this.generateSuggestions(input);
        // Implementation would show dropdown with suggestions
    }
    
    generateSuggestions(input) {
        const suggestions = [];
        const words = input.toLowerCase().split(' ');
        const lastWord = words[words.length - 1];
        
        // Suggest stroke types
        const strokeTypes = ['forehand', 'backhand', 'serve', 'volley', 'overhead'];
        strokeTypes.forEach(type => {
            if (type.startsWith(lastWord)) {
                suggestions.push(input.replace(lastWord, type));
            }
        });
        
        return suggestions;
    }
    
    // Helper methods
    getMostCommonOutcome(strokes) {
        const outcomes = {};
        strokes.forEach(s => {
            outcomes[s.outcome] = (outcomes[s.outcome] || 0) + 1;
        });
        
        return Object.keys(outcomes).reduce((a, b) => 
            outcomes[a] > outcomes[b] ? a : b, 'unknown');
    }
    
    getStrokeTypeDistribution(strokes) {
        const types = {};
        strokes.forEach(s => {
            types[s.stroke_type] = (types[s.stroke_type] || 0) + 1;
        });
        
        return Object.entries(types)
            .map(([type, count]) => ({
                type,
                count,
                percentage: ((count / strokes.length) * 100).toFixed(1)
            }))
            .sort((a, b) => b.count - a.count);
    }
    
    getZoneDistribution(strokes) {
        const zones = {};
        strokes.forEach(s => {
            zones[s.court_zone] = (zones[s.court_zone] || 0) + 1;
        });
        
        return Object.entries(zones)
            .map(([zone, count]) => ({ zone, count }))
            .sort((a, b) => b.count - a.count);
    }
    
    getAveragePressure(strokes) {
        if (strokes.length === 0) return 0;
        return strokes.reduce((sum, s) => sum + (s.pressure_index || 0), 0) / strokes.length;
    }
    
    getAveragePosition(positions) {
        if (positions.length === 0) return 'N/A';
        
        const avgX = positions.reduce((sum, p) => sum + p.x, 0) / positions.length;
        const avgY = positions.reduce((sum, p) => sum + p.y, 0) / positions.length;
        
        return `(${avgX.toFixed(2)}, ${avgY.toFixed(2)})`;
    }
    
    calculateErrorRate(errors) {
        const totalShots = this.strokeData.length;
        return totalShots > 0 ? ((errors.length / totalShots) * 100).toFixed(1) : 0;
    }
    
    calculateWinnerRate(winners) {
        const totalShots = this.strokeData.length;
        return totalShots > 0 ? ((winners.length / totalShots) * 100).toFixed(1) : 0;
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

// CSS for search interface
const searchStyles = `
    .pattern-search-container {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .search-header h3 {
        color: #00d4ff;
        margin-bottom: 8px;
        font-size: 20px;
    }
    
    .search-header p {
        color: rgba(255,255,255,0.7);
        margin-bottom: 20px;
    }
    
    .search-input-container {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .search-input {
        flex: 1;
        padding: 12px 16px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        color: white;
        font-size: 16px;
    }
    
    .search-input::placeholder {
        color: rgba(255,255,255,0.5);
    }
    
    .search-btn {
        padding: 12px 24px;
        background: #00d4ff;
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .search-btn:hover {
        background: #0099cc;
        transform: translateY(-1px);
    }
    
    .sample-queries {
        margin-bottom: 24px;
    }
    
    .sample-queries-header {
        color: rgba(255,255,255,0.8);
        margin-bottom: 12px;
        font-size: 14px;
    }
    
    .sample-query-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .sample-query {
        background: rgba(0,212,255,0.2);
        color: #00d4ff;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .sample-query:hover {
        background: rgba(0,212,255,0.3);
        transform: translateY(-1px);
    }
    
    .search-result-card {
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .result-header h4 {
        color: #00d4ff;
        margin-bottom: 8px;
    }
    
    .result-summary {
        color: rgba(255,255,255,0.8);
        margin-bottom: 16px;
    }
    
    .result-insights h5 {
        color: white;
        margin-bottom: 8px;
    }
    
    .result-insights ul {
        color: rgba(255,255,255,0.8);
        margin-bottom: 16px;
    }
    
    .result-insights li {
        margin-bottom: 4px;
    }
    
    .result-actions {
        display: flex;
        gap: 12px;
    }
    
    .action-btn {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .action-btn:hover {
        background: rgba(255,255,255,0.2);
        border-color: #00d4ff;
    }
    
    .search-history {
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .history-header {
        color: rgba(255,255,255,0.8);
        margin-bottom: 12px;
        font-size: 14px;
    }
    
    .history-item {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        background: rgba(255,255,255,0.1);
    }
    
    .history-query {
        color: #00d4ff;
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .history-summary {
        color: rgba(255,255,255,0.7);
        font-size: 12px;
        margin-bottom: 4px;
    }
    
    .history-time {
        color: rgba(255,255,255,0.5);
        font-size: 11px;
    }
    
    .search-error {
        background: rgba(255,59,48,0.1);
        border: 1px solid rgba(255,59,48,0.3);
        border-radius: 12px;
        padding: 16px;
        color: #ff3b30;
    }
`;

// Inject styles
if (!document.getElementById('search-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'search-styles';
    styleSheet.textContent = searchStyles;
    document.head.appendChild(styleSheet);
}

// Export for use
window.TennisPatternSearchEngine = TennisPatternSearchEngine;
