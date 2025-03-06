import os
import time
from pathlib import Path



from parsers.table_parser import Table, dataframe_to_json
from parsers.image_ocr import convert_image_to_json
from parsers.json_formatter import save_json
from utils.file_handler import get_data_from_pickling, save_data_from_pickling
from utils.logger import init_logger
from utils.constants import DATA_DIR, OUTPUT_DIR


logger = init_logger(__file__, "DEBUG")


def main():
    if os.name != "nt":
        try:
            # Linux나 macOS 환경에서는 import 안하도록
            from parsers.process_hwp_docs import HwpController
            hwp_ctrl = HwpController()

            for hwp_path in DATA_DIR.rglob("*.hwp"):
                output_path = OUTPUT_DIR / hwp_path.parent.stem

                components = hwp_ctrl.get_tag_from_html(hwp_path)
                components['content'] = hwp_ctrl.extract_text()
                
                if not output_path.exists():
                    os.makedirs(output_path)
                save_data_from_pickling(output_path / f'{hwp_path.stem}.pickle', components)
                
            del hwp_ctrl
        except ImportError:
            logger.error("please install pyhwpx")
    else:
        output_path = OUTPUT_DIR / "공업수학(KREYSZIG)_정진교" / "23강.pickle"
        print(get_data_from_pickling(output_path))

    # print(data)

    # total_tables = []
    # pickling_data = dict()
    
    # total_time = 0
    # docs_cnt = 0

    # # 결과를 담을 DIR 생성
    # if not OUTPUT_DIR.exists():
    #     OUTPUT_DIR.mkdir(parents=True)

    # for hwp_path in DATA_DIR.rglob("*.hwp"):
    #     hwp.open(hwp_path.as_posix())
    #     logger.info(f"Hwp {hwp_path} loding")

    #     txt = extract_text_exclude_table(hwp)
    #     one_file_table_list = []
    #     one_file_images = {}
    #     one_file_equations = []
    #     start = time.time()
    #     docs_cnt += 1

    #     for ctrl in hwp.ctrl_list:
    #         if ctrl.UserDesc in CTRL_TYPES:
    #             # 글자처럼 취급 적용 (속성 미적용시 표를 넘어가기도 함)
    #             prop = ctrl.Properties
    #             prop.SetItem("TreatAsChar", True)
    #             ctrl.Properties = prop

    #             # hwp로 현재 ctrl 위치에 있는 부분 복사
    #             hwp.SetPosBySet(ctrl.GetAnchorPos(0))
    #             hwp.HAction.Run("SelectCtrlFront")
    #             hwp.HAction.Run("Copy")

    #             if ctrl.UserDesc == "표":
    #                 try:
    #                     html = get_table_from_clipboard()
    #                     table_df = pd.read_html(io.StringIO(html))[0]
    #                     row_num, col_num = table_df.shape
                            
    #                 except BaseException as e:
    #                     logger.error(f"TableExtractionError: Failed to extract table: {e}")
    #                     continue

    #                 if not row_num or not col_num:
    #                     continue

    #                 table = Table(html=html, col=col_num, row=row_num)
    #                 one_file_table_list.append(table)
            
    #             elif ctrl.UserDesc == "그림":
    #                 try:
    #                     img_tmp_path = Path(get_image_from_clipboard())
    #                     if not img_tmp_path:
    #                         continue   
    #                     one_file_images[str(img_tmp_path)] = ''      

    #                 except Exception as e:
    #                     logger.error(f"Image Error: {str(e)}")

    #             elif ctrl.UserDesc == "수식":
    #                 eqn_string = ctrl.Properties.Item("String")
    #                 hwp.SetPosBySet(ctrl.GetAnchorPos(0))
    #                 hwp.HAction.Run("MoveRight")
    #                 hwp.HAction.Run("BreakPara")
    #                 one_file_equations.append(eqn_string)

    #     end = time.time()
    #     total_time += (end - start)

    #     pickling_data['content'] = txt
    #     pickling_data['images'] = one_file_images
    #     pickling_data['equals'] = one_file_equations
    #     pickling_data['time'] = end-start

    #     total_tables.extend(one_file_table_list)

    # save_data_from_pickling(OUTPUT_DIR / 'pickling' / f'{hwp_path.stem}.pickle', pickling_data)

    # if docs_cnt != 0:
    #     mean_time = total_time / docs_cnt
    #     logger.info(f"Process time: {mean_time}")

if __name__ == "__main__":
    main()