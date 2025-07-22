import io
import csv
import json
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    async def export_to_pdf(self, data: Dict[str, Any], export_type: str) -> bytes:
        """Export data to PDF format"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            story = []
            
            if export_type == "forecast":
                story = await self._build_forecast_pdf(data, story)
            elif export_type == "backtest":
                story = await self._build_backtest_pdf(data, story)
            
            doc.build(story)
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            print(f"PDF export error: {e}")
            return b""
    
    async def export_to_csv(self, data: Dict[str, Any], export_type: str) -> bytes:
        """Export data to CSV format"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            if export_type == "forecast":
                await self._build_forecast_csv(data, writer)
            elif export_type == "backtest":
                await self._build_backtest_csv(data, writer)
            
            csv_data = output.getvalue().encode('utf-8')
            output.close()
            
            return csv_data
            
        except Exception as e:
            print(f"CSV export error: {e}")
            return b""
    
    async def generate_summary(self, data: Dict[str, Any], export_type: str) -> str:
        """Generate a shareable text summary"""
        try:
            if export_type == "forecast":
                return await self._build_forecast_summary(data)
            elif export_type == "backtest":
                return await self._build_backtest_summary(data)
            
            return "Summary generation failed"
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return "Summary generation failed"
    
    async def _build_forecast_pdf(self, data: Dict[str, Any], story: list) -> list:
        """Build PDF content for forecast report"""
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
        )
        
        story.append(Paragraph("Trading Forecast Report", title_style))
        story.append(Spacer(1, 12))
        
        # Strategy and Asset info
        story.append(Paragraph(f"<b>Strategy:</b> {data.get('strategy', {}).get('name', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Asset:</b> {data.get('asset', {}).get('symbol', 'N/A')} - {data.get('asset', {}).get('name', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Confidence', f"{data.get('confidence', 0):.1f}%"],
            ['Expected Return', f"${data.get('expected_return', 0):,.2f}"],
            ['Win Probability', f"{data.get('win_probability', 0):.1f}%"],
            ['Risk/Reward Ratio', f"{data.get('reward_risk_ratio', 0):.2f}:1"],
            ['Valid Signal', 'Yes' if data.get('is_valid', False) else 'No']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Entry points
        if data.get('entry_points'):
            story.append(Paragraph("<b>Suggested Entry Points:</b>", self.styles['Heading2']))
            for i, price in enumerate(data['entry_points']):
                story.append(Paragraph(f"• Entry {i+1}: ${price:.2f}", self.styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Reasoning
        if data.get('reasoning'):
            story.append(Paragraph("<b>Analysis:</b>", self.styles['Heading2']))
            story.append(Paragraph(data['reasoning'], self.styles['Normal']))
        
        return story
    
    async def _build_backtest_pdf(self, data: Dict[str, Any], story: list) -> list:
        """Build PDF content for backtest report"""
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
        )
        
        story.append(Paragraph("Backtest Results Report", title_style))
        story.append(Spacer(1, 12))
        
        # Basic info
        story.append(Paragraph(f"<b>Strategy:</b> {data.get('strategy', {}).get('name', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Asset:</b> {data.get('asset', {}).get('symbol', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Period:</b> {data.get('period', {}).get('start', 'N/A')} to {data.get('period', {}).get('end', 'N/A')}", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Performance metrics table
        performance_data = [
            ['Metric', 'Value'],
            ['Total Return', f"{data.get('total_return', 0):.2f}%"],
            ['Win Rate', f"{data.get('win_rate', 0):.1f}%"],
            ['Total Trades', str(data.get('total_trades', 0))],
            ['Sharpe Ratio', f"{data.get('sharpe_ratio', 0):.2f}"],
            ['Max Drawdown', f"{data.get('max_drawdown', 0):.2f}%"],
            ['Profit Factor', f"{data.get('profit_factor', 0):.2f}"]
        ]
        
        performance_table = Table(performance_data, colWidths=[2*inch, 2*inch])
        performance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(performance_table)
        
        return story
    
    async def _build_forecast_csv(self, data: Dict[str, Any], writer) -> None:
        """Build CSV content for forecast data"""
        writer.writerow(['Forecast Report'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Basic info
        writer.writerow(['Strategy', data.get('strategy', {}).get('name', 'N/A')])
        writer.writerow(['Asset Symbol', data.get('asset', {}).get('symbol', 'N/A')])
        writer.writerow(['Asset Name', data.get('asset', {}).get('name', 'N/A')])
        writer.writerow([])
        
        # Metrics
        writer.writerow(['Metrics'])
        writer.writerow(['Confidence (%)', data.get('confidence', 0)])
        writer.writerow(['Expected Return ($)', data.get('expected_return', 0)])
        writer.writerow(['Win Probability (%)', data.get('win_probability', 0)])
        writer.writerow(['Risk/Reward Ratio', data.get('reward_risk_ratio', 0)])
        writer.writerow(['Valid Signal', 'Yes' if data.get('is_valid', False) else 'No'])
        writer.writerow([])
        
        # Entry points
        if data.get('entry_points'):
            writer.writerow(['Entry Points'])
            for i, price in enumerate(data['entry_points']):
                writer.writerow([f'Entry {i+1}', price])
    
    async def _build_backtest_csv(self, data: Dict[str, Any], writer) -> None:
        """Build CSV content for backtest data"""
        writer.writerow(['Backtest Report'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Performance metrics
        writer.writerow(['Performance Metrics'])
        writer.writerow(['Total Return (%)', data.get('total_return', 0)])
        writer.writerow(['Win Rate (%)', data.get('win_rate', 0)])
        writer.writerow(['Total Trades', data.get('total_trades', 0)])
        writer.writerow(['Sharpe Ratio', data.get('sharpe_ratio', 0)])
        writer.writerow(['Max Drawdown (%)', data.get('max_drawdown', 0)])
        writer.writerow(['Profit Factor', data.get('profit_factor', 0)])
        writer.writerow([])
        
        # Trades
        if data.get('trades'):
            writer.writerow(['Trade History'])
            writer.writerow(['Entry Date', 'Exit Date', 'Entry Price', 'Exit Price', 'PnL', 'Type', 'Reason'])
            for trade in data['trades']:
                writer.writerow([
                    trade.get('entry_date', ''),
                    trade.get('exit_date', ''),
                    trade.get('entry_price', 0),
                    trade.get('exit_price', 0),
                    trade.get('pnl', 0),
                    trade.get('type', ''),
                    trade.get('reason', '')
                ])
    
    async def _build_forecast_summary(self, data: Dict[str, Any]) -> str:
        """Build text summary for forecast"""
        strategy_name = data.get('strategy', {}).get('name', 'Unknown Strategy')
        asset_symbol = data.get('asset', {}).get('symbol', 'Unknown Asset')
        confidence = data.get('confidence', 0)
        expected_return = data.get('expected_return', 0)
        win_prob = data.get('win_probability', 0)
        risk_reward = data.get('reward_risk_ratio', 0)
        is_valid = data.get('is_valid', False)
        
        status = "VALID" if is_valid else "INVALID"
        
        summary = f"""
🎯 TRADING FORECAST - {asset_symbol}

Strategy: {strategy_name}
Status: {status}
Confidence: {confidence:.1f}%
Expected Return: ${expected_return:,.2f}
Win Probability: {win_prob:.1f}%
Risk/Reward: {risk_reward:.2f}:1

Entry Points: {', '.join([f'${p:.2f}' for p in data.get('entry_points', [])])}

Analysis: {data.get('reasoning', 'No analysis available')}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return summary
    
    async def _build_backtest_summary(self, data: Dict[str, Any]) -> str:
        """Build text summary for backtest"""
        strategy_name = data.get('strategy', {}).get('name', 'Unknown Strategy')
        asset_symbol = data.get('asset', {}).get('symbol', 'Unknown Asset')
        total_return = data.get('total_return', 0)
        win_rate = data.get('win_rate', 0)
        total_trades = data.get('total_trades', 0)
        sharpe = data.get('sharpe_ratio', 0)
        max_dd = data.get('max_drawdown', 0)
        
        summary = f"""
📊 BACKTEST RESULTS - {asset_symbol}

Strategy: {strategy_name}
Total Return: {total_return:.2f}%
Win Rate: {win_rate:.1f}%
Total Trades: {total_trades}
Sharpe Ratio: {sharpe:.2f}
Max Drawdown: {max_dd:.2f}%

Performance Rating: {'Excellent' if total_return > 20 else 'Good' if total_return > 10 else 'Fair' if total_return > 0 else 'Poor'}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return summary
