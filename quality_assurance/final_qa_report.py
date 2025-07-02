#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail 最終品質保証レポート生成

Task 15: 最終品質保証テストとドキュメント更新
プロジェクト全体の完成度を評価し、リリース準備状況を確認します。
"""

import os
import sys
import json
import subprocess
import ast
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


class WabiMailQualityAssurance:
    """WabiMail 品質保証システム"""
    
    def __init__(self):
        """初期化"""
        self.qa_start_time = datetime.now()
        self.results = {
            "project_info": {},
            "code_quality": {},
            "documentation": {},
            "build_artifacts": {},
            "test_coverage": {},
            "release_readiness": {}
        }
        
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def analyze_project_structure(self):
        """プロジェクト構造分析"""
        self.log("📁 プロジェクト構造分析")
        
        # ディレクトリ構造確認
        key_directories = [
            "src", "tests", "docs", "resources", "installer", 
            "build_config", "quality_assurance"
        ]
        
        structure_analysis = {}
        total_files = 0
        total_lines = 0
        
        for directory in key_directories:
            dir_path = PROJECT_ROOT / directory
            if dir_path.exists():
                files = list(dir_path.rglob("*.py"))
                file_count = len(files)
                line_count = sum(len(f.read_text(encoding='utf-8', errors='ignore').splitlines()) 
                               for f in files if f.is_file())
                
                structure_analysis[directory] = {
                    "exists": True,
                    "file_count": file_count,
                    "line_count": line_count
                }
                total_files += file_count
                total_lines += line_count
            else:
                structure_analysis[directory] = {"exists": False}
        
        # 重要ファイル確認
        critical_files = [
            "src/main.py", "config.yaml", "README.md", "LICENSE",
            "WabiMail.spec", "requirements.txt"
        ]
        
        file_analysis = {}
        for file_path in critical_files:
            full_path = PROJECT_ROOT / file_path
            file_analysis[file_path] = {
                "exists": full_path.exists(),
                "size_kb": round(full_path.stat().st_size / 1024, 2) if full_path.exists() else 0
            }
        
        self.results["project_info"] = {
            "total_files": total_files,
            "total_lines": total_lines,
            "directory_structure": structure_analysis,
            "critical_files": file_analysis,
            "analysis_date": self.qa_start_time.isoformat()
        }
        
        self.log(f"✅ プロジェクト分析完了: {total_files}ファイル, {total_lines}行")
    
    def analyze_code_quality(self):
        """コード品質分析"""
        self.log("🔍 コード品質分析")
        
        python_files = list(PROJECT_ROOT.rglob("*.py"))
        
        quality_metrics = {
            "total_python_files": len(python_files),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "docstring_coverage": 0,
            "complexity_analysis": {},
            "import_analysis": {}
        }
        
        functions_with_docs = 0
        classes_with_docs = 0
        import_counts = defaultdict(int)
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                quality_metrics["total_lines"] += len(lines)
                
                # AST解析
                try:
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            quality_metrics["total_functions"] += 1
                            if ast.get_docstring(node):
                                functions_with_docs += 1
                        
                        elif isinstance(node, ast.ClassDef):
                            quality_metrics["total_classes"] += 1
                            if ast.get_docstring(node):
                                classes_with_docs += 1
                        
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    import_counts[alias.name] += 1
                            else:  # ImportFrom
                                module = node.module or ""
                                import_counts[module] += 1
                
                except SyntaxError:
                    self.log(f"⚠️  構文エラー: {py_file}")
                    
            except Exception as e:
                self.log(f"⚠️  ファイル読み込みエラー {py_file}: {e}")
        
        # ドキュメント率計算
        total_definitions = quality_metrics["total_functions"] + quality_metrics["total_classes"]
        documented_definitions = functions_with_docs + classes_with_docs
        
        if total_definitions > 0:
            quality_metrics["docstring_coverage"] = round(
                (documented_definitions / total_definitions) * 100, 1
            )
        
        # インポート分析（上位10件）
        quality_metrics["import_analysis"] = dict(
            sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # 複雑度分析（ファイルサイズベース）
        large_files = []
        for py_file in python_files:
            line_count = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
            if line_count > 200:  # 200行超の大きなファイル
                large_files.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "lines": line_count
                })
        
        quality_metrics["complexity_analysis"] = {
            "large_files": large_files,
            "average_file_size": round(
                quality_metrics["total_lines"] / max(quality_metrics["total_python_files"], 1), 1
            )
        }
        
        self.results["code_quality"] = quality_metrics
        
        self.log(f"✅ コード品質分析完了:")
        self.log(f"   📊 {quality_metrics['total_python_files']}ファイル, {quality_metrics['total_lines']}行")
        self.log(f"   📝 ドキュメント率: {quality_metrics['docstring_coverage']}%")
        self.log(f"   🔧 {quality_metrics['total_functions']}関数, {quality_metrics['total_classes']}クラス")
    
    def analyze_documentation(self):
        """ドキュメント分析"""
        self.log("📚 ドキュメント分析")
        
        # ドキュメントファイル確認
        doc_files = {
            "README.md": PROJECT_ROOT / "README.md",
            "LICENSE": PROJECT_ROOT / "LICENSE", 
            "config.yaml": PROJECT_ROOT / "config.yaml",
            "requirements.txt": PROJECT_ROOT / "requirements.txt",
            "build_instructions.md": PROJECT_ROOT / "docs" / "build_instructions.md",
            "installer_README.md": PROJECT_ROOT / "installer" / "README.md"
        }
        
        doc_analysis = {}
        total_doc_size = 0
        
        for doc_name, doc_path in doc_files.items():
            if doc_path.exists():
                content = doc_path.read_text(encoding='utf-8', errors='ignore')
                lines = len(content.splitlines())
                size_kb = round(doc_path.stat().st_size / 1024, 2)
                
                doc_analysis[doc_name] = {
                    "exists": True,
                    "lines": lines,
                    "size_kb": size_kb,
                    "char_count": len(content)
                }
                total_doc_size += size_kb
            else:
                doc_analysis[doc_name] = {"exists": False}
        
        # 開発ノート分析
        note_dir = PROJECT_ROOT / "docs" / "note" / "development"
        blog_dir = PROJECT_ROOT / "docs" / "note" / "blog"
        
        development_notes = len(list(note_dir.glob("*.md"))) if note_dir.exists() else 0
        blog_posts = len(list(blog_dir.glob("*.md"))) if blog_dir.exists() else 0
        
        self.results["documentation"] = {
            "core_documents": doc_analysis,
            "total_doc_size_kb": round(total_doc_size, 2),
            "development_notes": development_notes,
            "blog_posts": blog_posts,
            "documentation_completeness": self._calculate_doc_completeness(doc_analysis)
        }
        
        self.log(f"✅ ドキュメント分析完了:")
        self.log(f"   📖 コアドキュメント: {sum(1 for d in doc_analysis.values() if d.get('exists', False))}/{len(doc_analysis)}")
        self.log(f"   📝 開発ノート: {development_notes}件")
        self.log(f"   📰 ブログ記事: {blog_posts}件")
    
    def _calculate_doc_completeness(self, doc_analysis):
        """ドキュメント完成度計算"""
        required_docs = ["README.md", "LICENSE", "config.yaml"]
        existing_required = sum(1 for doc in required_docs if doc_analysis.get(doc, {}).get('exists', False))
        
        optional_docs = ["requirements.txt", "build_instructions.md", "installer_README.md"]
        existing_optional = sum(1 for doc in optional_docs if doc_analysis.get(doc, {}).get('exists', False))
        
        # 必須ドキュメント100% + オプション50%重み
        total_score = (existing_required / len(required_docs)) * 100
        optional_score = (existing_optional / len(optional_docs)) * 50
        
        return round(min(total_score + optional_score, 100), 1)
    
    def analyze_build_artifacts(self):
        """ビルド成果物分析"""
        self.log("🔨 ビルド成果物分析")
        
        artifacts = {}
        
        # 実行ファイル確認
        exe_files = list(PROJECT_ROOT.glob("dist/*"))
        if exe_files:
            artifacts["executables"] = []
            for exe_file in exe_files:
                if exe_file.is_file():
                    size_mb = round(exe_file.stat().st_size / (1024 * 1024), 2)
                    artifacts["executables"].append({
                        "name": exe_file.name,
                        "size_mb": size_mb,
                        "path": str(exe_file.relative_to(PROJECT_ROOT))
                    })
        
        # PyInstaller Spec ファイル
        spec_file = PROJECT_ROOT / "WabiMail.spec"
        artifacts["pyinstaller_spec"] = {
            "exists": spec_file.exists(),
            "size_kb": round(spec_file.stat().st_size / 1024, 2) if spec_file.exists() else 0
        }
        
        # Inno Setup スクリプト
        iss_file = PROJECT_ROOT / "installer" / "wabimail_installer.iss"
        artifacts["inno_setup_script"] = {
            "exists": iss_file.exists(),
            "size_kb": round(iss_file.stat().st_size / 1024, 2) if iss_file.exists() else 0
        }
        
        # ビルドスクリプト
        build_scripts = [
            "build_simple.py", "build_exe.py", "installer/build_installer.py"
        ]
        
        artifacts["build_scripts"] = {}
        for script in build_scripts:
            script_path = PROJECT_ROOT / script
            artifacts["build_scripts"][script] = {
                "exists": script_path.exists(),
                "size_kb": round(script_path.stat().st_size / 1024, 2) if script_path.exists() else 0
            }
        
        # テストスクリプト
        test_scripts = [
            "test_executable.py", "installer/test_installer.py", "tests/test_integration.py"
        ]
        
        artifacts["test_scripts"] = {}
        for script in test_scripts:
            script_path = PROJECT_ROOT / script
            artifacts["test_scripts"][script] = {
                "exists": script_path.exists(),
                "size_kb": round(script_path.stat().st_size / 1024, 2) if script_path.exists() else 0
            }
        
        self.results["build_artifacts"] = artifacts
        
        # 結果表示
        exe_count = len(artifacts.get("executables", []))
        build_script_count = sum(1 for s in artifacts["build_scripts"].values() if s["exists"])
        test_script_count = sum(1 for s in artifacts["test_scripts"].values() if s["exists"])
        
        self.log(f"✅ ビルド成果物分析完了:")
        self.log(f"   🚀 実行ファイル: {exe_count}個")
        self.log(f"   🔧 ビルドスクリプト: {build_script_count}/{len(build_scripts)}個")
        self.log(f"   🧪 テストスクリプト: {test_script_count}/{len(test_scripts)}個")
    
    def analyze_test_coverage(self):
        """テストカバレッジ分析"""
        self.log("🧪 テストカバレッジ分析")
        
        # テストファイル検索
        test_files = list(PROJECT_ROOT.rglob("test_*.py")) + list(PROJECT_ROOT.rglob("*_test.py"))
        
        test_analysis = {
            "test_file_count": len(test_files),
            "test_categories": {},
            "integration_tests": False,
            "unit_tests": False,
            "build_tests": False,
            "installer_tests": False
        }
        
        for test_file in test_files:
            category = "other"
            if "integration" in test_file.name:
                category = "integration"
                test_analysis["integration_tests"] = True
            elif "unit" in test_file.name:
                category = "unit"
                test_analysis["unit_tests"] = True
            elif "executable" in test_file.name or "build" in test_file.name:
                category = "build"
                test_analysis["build_tests"] = True
            elif "installer" in test_file.name:
                category = "installer"
                test_analysis["installer_tests"] = True
            
            if category not in test_analysis["test_categories"]:
                test_analysis["test_categories"][category] = []
            
            test_analysis["test_categories"][category].append({
                "file": str(test_file.relative_to(PROJECT_ROOT)),
                "size_kb": round(test_file.stat().st_size / 1024, 2)
            })
        
        # テストカバレッジ推定
        src_files = len(list((PROJECT_ROOT / "src").rglob("*.py")))
        test_to_src_ratio = round(len(test_files) / max(src_files, 1), 2)
        
        test_analysis["coverage_estimation"] = {
            "test_to_source_ratio": test_to_src_ratio,
            "estimated_coverage": min(test_to_src_ratio * 100, 100)
        }
        
        self.results["test_coverage"] = test_analysis
        
        self.log(f"✅ テストカバレッジ分析完了:")
        self.log(f"   🧪 テストファイル: {len(test_files)}個")
        self.log(f"   📊 推定カバレッジ: {test_analysis['coverage_estimation']['estimated_coverage']:.1f}%")
        
        # テストタイプ表示
        test_types = [
            ("統合テスト", test_analysis["integration_tests"]),
            ("ビルドテスト", test_analysis["build_tests"]),
            ("インストーラーテスト", test_analysis["installer_tests"])
        ]
        
        for test_type, exists in test_types:
            status = "✅" if exists else "❌"
            self.log(f"   {status} {test_type}")
    
    def evaluate_release_readiness(self):
        """リリース準備状況評価"""
        self.log("🚀 リリース準備状況評価")
        
        readiness_criteria = {
            "core_functionality": self._check_core_functionality(),
            "documentation_quality": self._check_documentation_quality(),
            "build_system": self._check_build_system(),
            "test_coverage": self._check_test_coverage(),
            "code_quality": self._check_code_quality(),
            "deployment_readiness": self._check_deployment_readiness()
        }
        
        # 総合スコア計算
        scores = [criteria["score"] for criteria in readiness_criteria.values()]
        overall_score = round(sum(scores) / len(scores), 1)
        
        # リリース準備レベル判定
        if overall_score >= 90:
            readiness_level = "READY"
            readiness_message = "リリース準備完了"
        elif overall_score >= 80:
            readiness_level = "ALMOST_READY"
            readiness_message = "軽微な修正が必要"
        elif overall_score >= 70:
            readiness_level = "NEEDS_WORK"
            readiness_message = "追加作業が必要"
        else:
            readiness_level = "NOT_READY"
            readiness_message = "大幅な改善が必要"
        
        self.results["release_readiness"] = {
            "overall_score": overall_score,
            "readiness_level": readiness_level,
            "readiness_message": readiness_message,
            "criteria": readiness_criteria,
            "recommendations": self._generate_recommendations(readiness_criteria)
        }
        
        self.log(f"✅ リリース準備評価完了:")
        self.log(f"   📊 総合スコア: {overall_score}/100")
        self.log(f"   🎯 準備状況: {readiness_message}")
    
    def _check_core_functionality(self):
        """コア機能チェック"""
        # 重要ファイルの存在確認
        critical_files = [
            "src/main.py", "src/ui/main_window.py", "src/mail/imap_client.py",
            "src/mail/smtp_client.py", "src/auth/gmail_oauth.py"
        ]
        
        existing_files = sum(1 for f in critical_files if (PROJECT_ROOT / f).exists())
        score = round((existing_files / len(critical_files)) * 100, 1)
        
        return {
            "score": score,
            "details": f"{existing_files}/{len(critical_files)} コアファイル存在",
            "status": "GOOD" if score >= 80 else "NEEDS_IMPROVEMENT"
        }
    
    def _check_documentation_quality(self):
        """ドキュメント品質チェック"""
        doc_completeness = self.results["documentation"]["documentation_completeness"]
        
        return {
            "score": doc_completeness,
            "details": f"ドキュメント完成度 {doc_completeness}%",
            "status": "GOOD" if doc_completeness >= 80 else "NEEDS_IMPROVEMENT"
        }
    
    def _check_build_system(self):
        """ビルドシステムチェック"""
        required_build_files = [
            "WabiMail.spec", "build_simple.py", "build_exe.py", 
            "installer/wabimail_installer.iss", "installer/build_installer.py"
        ]
        
        existing_build_files = sum(1 for f in required_build_files if (PROJECT_ROOT / f).exists())
        score = round((existing_build_files / len(required_build_files)) * 100, 1)
        
        return {
            "score": score,
            "details": f"{existing_build_files}/{len(required_build_files)} ビルドファイル存在",
            "status": "GOOD" if score >= 80 else "NEEDS_IMPROVEMENT"
        }
    
    def _check_test_coverage(self):
        """テストカバレッジチェック"""
        test_coverage = self.results["test_coverage"]
        
        # テストタイプの存在確認
        test_types = [
            test_coverage["integration_tests"],
            test_coverage["build_tests"],
            test_coverage["installer_tests"]
        ]
        
        existing_test_types = sum(1 for t in test_types if t)
        score = round((existing_test_types / len(test_types)) * 100, 1)
        
        return {
            "score": score,
            "details": f"{existing_test_types}/{len(test_types)} テストタイプ実装",
            "status": "GOOD" if score >= 66 else "NEEDS_IMPROVEMENT"
        }
    
    def _check_code_quality(self):
        """コード品質チェック"""
        code_quality = self.results["code_quality"]
        
        # ドキュメント率とファイル数から品質スコア算出
        doc_coverage = code_quality["docstring_coverage"]
        avg_file_size = code_quality["complexity_analysis"]["average_file_size"]
        
        # 適切なファイルサイズ（50-300行）
        size_score = 100 if 50 <= avg_file_size <= 300 else max(0, 100 - abs(avg_file_size - 175))
        
        # 総合品質スコア
        score = round((doc_coverage + size_score) / 2, 1)
        
        return {
            "score": score,
            "details": f"ドキュメント率{doc_coverage}%, 平均ファイルサイズ{avg_file_size}行",
            "status": "GOOD" if score >= 70 else "NEEDS_IMPROVEMENT"
        }
    
    def _check_deployment_readiness(self):
        """デプロイ準備チェック"""
        # 配布に必要なファイル確認
        deployment_files = [
            "README.md", "LICENSE", "config.yaml"
        ]
        
        existing_deployment_files = sum(1 for f in deployment_files if (PROJECT_ROOT / f).exists())
        
        # 実行ファイルの存在確認
        has_executable = len(self.results["build_artifacts"].get("executables", [])) > 0
        
        # スコア算出
        file_score = (existing_deployment_files / len(deployment_files)) * 70
        exe_score = 30 if has_executable else 0
        score = round(file_score + exe_score, 1)
        
        return {
            "score": score,
            "details": f"{existing_deployment_files}/{len(deployment_files)} 配布ファイル, 実行ファイル{'あり' if has_executable else 'なし'}",
            "status": "GOOD" if score >= 80 else "NEEDS_IMPROVEMENT"
        }
    
    def _generate_recommendations(self, criteria):
        """改善提案生成"""
        recommendations = []
        
        for criterion_name, criterion_data in criteria.items():
            if criterion_data["status"] == "NEEDS_IMPROVEMENT":
                if criterion_name == "core_functionality":
                    recommendations.append("不足しているコアファイルを実装してください")
                elif criterion_name == "documentation_quality":
                    recommendations.append("ドキュメントの充実を図ってください")
                elif criterion_name == "build_system":
                    recommendations.append("ビルドシステムファイルを完成させてください")
                elif criterion_name == "test_coverage":
                    recommendations.append("テストカバレッジを向上させてください")
                elif criterion_name == "code_quality":
                    recommendations.append("コード品質（ドキュメント、構造）を改善してください")
                elif criterion_name == "deployment_readiness":
                    recommendations.append("配布準備ファイルを整備してください")
        
        if not recommendations:
            recommendations.append("すべての基準を満たしています。リリース準備完了です！")
        
        return recommendations
    
    def generate_comprehensive_report(self):
        """包括的レポート生成"""
        qa_end_time = datetime.now()
        qa_duration = qa_end_time - self.qa_start_time
        
        # 最終レポートデータ
        final_report = {
            "report_info": {
                "generated_at": qa_end_time.isoformat(),
                "analysis_duration_seconds": qa_duration.total_seconds(),
                "wabimail_version": "1.0.0",
                "analysis_tool": "WabiMail Quality Assurance System"
            },
            **self.results
        }
        
        # レポートファイル保存
        report_dir = PROJECT_ROOT / "quality_assurance" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.qa_start_time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"final_qa_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        # コンソールサマリー出力
        self._print_summary_report(final_report)
        
        self.log(f"📄 最終品質保証レポート保存: {report_file}")
        return report_file
    
    def _print_summary_report(self, report):
        """サマリーレポート表示"""
        print("\n" + "🌸" * 30)
        print("WabiMail 最終品質保証レポート")
        print("🌸" * 30)
        
        # プロジェクト概要
        project_info = report["project_info"]
        print(f"\n📊 プロジェクト概要:")
        print(f"  ・総ファイル数: {project_info['total_files']:,}")
        print(f"  ・総行数: {project_info['total_lines']:,}")
        
        # コード品質
        code_quality = report["code_quality"]
        print(f"\n🔍 コード品質:")
        print(f"  ・Pythonファイル: {code_quality['total_python_files']}")
        print(f"  ・関数数: {code_quality['total_functions']}")
        print(f"  ・クラス数: {code_quality['total_classes']}")
        print(f"  ・ドキュメント率: {code_quality['docstring_coverage']}%")
        
        # ドキュメント
        documentation = report["documentation"]
        print(f"\n📚 ドキュメント:")
        print(f"  ・完成度: {documentation['documentation_completeness']}%")
        print(f"  ・開発ノート: {documentation['development_notes']}件")
        print(f"  ・ブログ記事: {documentation['blog_posts']}件")
        
        # ビルド成果物
        build_artifacts = report["build_artifacts"]
        exe_count = len(build_artifacts.get("executables", []))
        print(f"\n🔨 ビルド成果物:")
        print(f"  ・実行ファイル: {exe_count}個")
        print(f"  ・PyInstaller Spec: {'✅' if build_artifacts['pyinstaller_spec']['exists'] else '❌'}")
        print(f"  ・Inno Setup: {'✅' if build_artifacts['inno_setup_script']['exists'] else '❌'}")
        
        # テストカバレッジ
        test_coverage = report["test_coverage"]
        print(f"\n🧪 テストカバレッジ:")
        print(f"  ・テストファイル: {test_coverage['test_file_count']}個")
        print(f"  ・統合テスト: {'✅' if test_coverage['integration_tests'] else '❌'}")
        print(f"  ・ビルドテスト: {'✅' if test_coverage['build_tests'] else '❌'}")
        print(f"  ・インストーラーテスト: {'✅' if test_coverage['installer_tests'] else '❌'}")
        
        # リリース準備状況
        release_readiness = report["release_readiness"]
        print(f"\n🚀 リリース準備状況:")
        print(f"  ・総合スコア: {release_readiness['overall_score']}/100")
        print(f"  ・準備レベル: {release_readiness['readiness_message']}")
        
        # 改善提案
        if release_readiness["recommendations"]:
            print(f"\n💡 改善提案:")
            for i, rec in enumerate(release_readiness["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "🌸" * 30)
        print("侘び寂びの美学に基づく品質保証完了")
        print("🌸" * 30 + "\n")
    
    def run(self):
        """メイン品質保証処理"""
        print("🌸 WabiMail 最終品質保証システム")
        print("=" * 60)
        print(f"分析開始: {self.qa_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # 1. プロジェクト構造分析
            self.analyze_project_structure()
            
            # 2. コード品質分析
            self.analyze_code_quality()
            
            # 3. ドキュメント分析
            self.analyze_documentation()
            
            # 4. ビルド成果物分析
            self.analyze_build_artifacts()
            
            # 5. テストカバレッジ分析
            self.analyze_test_coverage()
            
            # 6. リリース準備状況評価
            self.evaluate_release_readiness()
            
            # 7. 包括的レポート生成
            report_file = self.generate_comprehensive_report()
            
            return True
            
        except Exception as e:
            self.log(f"❌ 品質保証プロセスエラー: {e}")
            return False


def main():
    """メイン関数"""
    qa_system = WabiMailQualityAssurance()
    
    try:
        success = qa_system.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 品質保証プロセスが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()